# -*- coding: utf-8 -*-
"""MoneyTransfer external update engine v2.
Designed for the installed PyInstaller/Setup edition.  It is intentionally an
external module so it can itself be updated without rebuilding MoneyTransfer.exe.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get("MONEYTRANSFER_DATA_DIR", str(Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MoneyTransfer" / "Data"))).resolve()
DESKTOP_DB = Path(os.environ.get("MONEYTRANSFER_DESKTOP_DB", str(DATA_ROOT / "financial_pos.db"))).resolve()
SERVER_DATA = Path(os.environ.get("MONEYTRANSFER_SERVER_DATA_DIR", str(DATA_ROOT / "server"))).resolve()
BACKUP_ROOT = Path(os.environ.get("MONEYTRANSFER_BACKUP_DIR", str(DATA_ROOT / "backups"))).resolve()
UPDATE_ROOT = DATA_ROOT / "update_engine"

PROTECTED_PREFIXES = (
    "financial_pos.db",
    "server/data",
    "data",
    "backups",
    "updates/backups",
)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm(name):
    return name.replace("\\", "/").lstrip("./")


def _safe_members(z):
    for m in z.infolist():
        p = Path(m.filename)
        if p.is_absolute() or ".." in p.parts:
            raise ValueError("الحزمة تحتوي مساراً غير آمن")
        yield m


def _manifest(z):
    names = [_norm(n) for n in z.namelist()]
    if "update_manifest.json" not in names:
        raise ValueError("يجب أن يكون update_manifest.json في جذر حزمة التحديث")
    original = z.namelist()[names.index("update_manifest.json")]
    data = json.loads(z.read(original).decode("utf-8"))
    required = {"manifest_version", "product", "version", "api_version", "schema_version", "channel"}
    missing = required - set(data)
    if missing:
        raise ValueError("حقول Manifest ناقصة: " + ", ".join(sorted(missing)))
    if data.get("product") != "MoneyTransfer":
        raise ValueError("هذه الحزمة ليست لبرنامج MoneyTransfer")
    return data


def _is_protected(rel):
    r = _norm(rel).lower()
    for p in PROTECTED_PREFIXES:
        p = p.lower()
        if r == p or r.startswith(p + "/"):
            return True
    return False


def inspect_package(zip_path):
    zp = Path(zip_path)
    if not zp.is_file():
        raise ValueError("ملف التحديث غير موجود")
    if not zipfile.is_zipfile(zp):
        raise ValueError("الملف المختار ليس ZIP صالحاً")
    with zipfile.ZipFile(zp) as z:
        members = list(_safe_members(z))
        meta = _manifest(z)
        protected = []
        payload_files = []
        for m in members:
            if m.is_dir():
                continue
            rel = _norm(m.filename)
            if rel == "update_manifest.json":
                continue
            if _is_protected(rel):
                protected.append(rel)
            else:
                payload_files.append(rel)
        if protected:
            raise ValueError("تم رفض الحزمة لأنها تحاول استبدال بيانات المستخدم: " + ", ".join(protected[:5]))
        if not payload_files:
            raise ValueError("حزمة التحديث لا تحتوي ملفات برنامج")
    result = dict(meta)
    result["package_sha256"] = sha256(zp)
    result["file_count"] = len(payload_files)
    return result


def _backup_user_data(stamp):
    dest = BACKUP_ROOT / ("pre_update_" + stamp)
    dest.mkdir(parents=True, exist_ok=False)
    if DESKTOP_DB.is_file():
        shutil.copy2(DESKTOP_DB, dest / "financial_pos.db")
    if SERVER_DATA.is_dir():
        shutil.copytree(SERVER_DATA, dest / "server_data")
    return dest


def _ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def launch_update(zip_path):
    meta = inspect_package(zip_path)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    UPDATE_ROOT.mkdir(parents=True, exist_ok=True)
    stage = UPDATE_ROOT / "staged" / (str(meta["version"]) + "_" + stamp)
    stage.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(zip_path) as z:
        members = list(_safe_members(z))
        z.extractall(stage, members=members)

    # V8.0.1.1 bridge: optional deterministic text patches.
    # A patch package can contain text_patch.json instead of an entire large
    # source file. Each replacement must match exactly, otherwise the update
    # is aborted before the installed program is changed.
    patch_spec = stage / "text_patch.json"
    if patch_spec.is_file():
        spec = json.loads(patch_spec.read_text(encoding="utf-8-sig"))
        patches = spec.get("patches", []) if isinstance(spec, dict) else []
        if not isinstance(patches, list) or not patches:
            raise ValueError("ملف text_patch.json لا يحتوي تعليمات تحديث صالحة")
        for item in patches:
            if not isinstance(item, dict):
                raise ValueError("تعليمات التحديث النصي غير صالحة")
            rel = _norm(str(item.get("path", "")))
            if not rel or _is_protected(rel):
                raise ValueError("مسار التحديث النصي غير مسموح: " + rel)
            source = (ROOT / rel).resolve()
            try:
                source.relative_to(ROOT.resolve())
            except ValueError:
                raise ValueError("مسار التحديث النصي خارج مجلد البرنامج")
            if not source.is_file():
                raise ValueError("ملف التحديث النصي غير موجود في البرنامج: " + rel)
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            text = source.read_text(encoding="utf-8")
            reps = item.get("replacements", [])
            if not isinstance(reps, list) or not reps:
                raise ValueError("لا توجد استبدالات للملف: " + rel)
            for rep in reps:
                if not isinstance(rep, dict) or "old" not in rep or "new" not in rep:
                    raise ValueError("تعليمة استبدال غير صالحة للملف: " + rel)
                old = str(rep["old"])
                new = str(rep["new"])
                expected_count = int(rep.get("count", 1))
                actual_count = text.count(old)
                if actual_count != expected_count:
                    raise ValueError(
                        f"تعذر تطبيق التحديث بأمان على {rel}: المتوقع {expected_count} تطابق، الموجود {actual_count}"
                    )
                text = text.replace(old, new, expected_count)
            target.write_text(text, encoding="utf-8")
        patch_spec.unlink(missing_ok=True)

    manifest = stage / "update_manifest.json"
    manifest.unlink(missing_ok=True)
    backup = _backup_user_data(stamp)
    program_backup = UPDATE_ROOT / "program_backups" / stamp
    result_file = UPDATE_ROOT / "last_update_result.json"
    script = UPDATE_ROOT / ("apply_" + stamp + ".ps1")
    exe = ROOT / "MoneyTransfer.exe"
    parent_pid = os.getpid()

    # The helper runs outside MoneyTransfer, waits for the UI to exit, stops the
    # local API child if necessary, backs up changed program files, applies the
    # staged payload, then starts the application again.
    ps = f'''$ErrorActionPreference = "Stop"\n$root = {_ps_quote(ROOT)}\n$stage = {_ps_quote(stage)}\n$backup = {_ps_quote(program_backup)}\n$result = {_ps_quote(result_file)}\n$exe = {_ps_quote(exe)}\n$parentPid = {parent_pid}\n$version = {_ps_quote(meta['version'])}\nStart-Sleep -Milliseconds 900\ntry {{ Wait-Process -Id $parentPid -Timeout 20 -ErrorAction SilentlyContinue }} catch {{}}\n# Stop any remaining MoneyTransfer process from this exact installation (normally the API child).\ntry {{\n  Get-CimInstance Win32_Process -Filter "Name='MoneyTransfer.exe'" | ForEach-Object {{\n    if ($_.ExecutablePath -and ([System.IO.Path]::GetFullPath($_.ExecutablePath) -eq [System.IO.Path]::GetFullPath($exe))) {{\n      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue\n    }}\n  }}\n}} catch {{}}\nStart-Sleep -Milliseconds 500\nNew-Item -ItemType Directory -Force -Path $backup | Out-Null\n$changed = @()\ntry {{\n  Get-ChildItem -Path $stage -File -Recurse | ForEach-Object {{\n    $rel = $_.FullName.Substring($stage.Length).TrimStart('\\','/')\n    $dst = Join-Path $root $rel\n    $rb = Join-Path $backup $rel\n    if (Test-Path $dst) {{\n      New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($rb)) | Out-Null\n      Copy-Item -LiteralPath $dst -Destination $rb -Force\n    }}\n    New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($dst)) | Out-Null\n    Copy-Item -LiteralPath $_.FullName -Destination $dst -Force\n    $changed += $rel\n  }}\n  @{{ok=$true; version=$version; applied_at=(Get-Date).ToString('s'); files=$changed; program_backup=$backup}} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $result -Encoding UTF8\n  Start-Process -FilePath $exe -WorkingDirectory $root\n}} catch {{\n  $err = $_.Exception.Message\n  # Roll back every file that had a previous copy. New files are left only if rollback cannot identify them safely.\n  if (Test-Path $backup) {{\n    Get-ChildItem -Path $backup -File -Recurse | ForEach-Object {{\n      $rel = $_.FullName.Substring($backup.Length).TrimStart('\\','/')\n      $dst = Join-Path $root $rel\n      New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($dst)) | Out-Null\n      Copy-Item -LiteralPath $_.FullName -Destination $dst -Force\n    }}\n  }}\n  @{{ok=$false; version=$version; applied_at=(Get-Date).ToString('s'); error=$err; program_backup=$backup}} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $result -Encoding UTF8\n  Start-Process -FilePath $exe -WorkingDirectory $root\n}}\n'''
    script.write_text(ps, encoding="utf-8-sig")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen([
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden",
        "-File", str(script)
    ], cwd=str(ROOT), creationflags=flags)
    return {"version": meta["version"], "backup": str(backup), "stage": str(stage), "sha256": meta["package_sha256"]}

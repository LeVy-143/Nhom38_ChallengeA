"""Persistent conventions. Atomic writes; superseded values stay in history."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile


def memory_path():
    return Path(os.getenv('AGENT_MEMORY_FILE', str(Path(__file__).with_name('project_memory.json'))))


def load_conventions():
    path = memory_path()
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or any(
        not isinstance(entry, dict) or not isinstance(entry.get('value'), str)
        or not isinstance(entry.get('history', []), list)
        for entry in data.values()
    ):
        raise ValueError('Invalid memory schema; existing file was not changed.')
    return data


def save_convention(key, value):
    if not isinstance(key, str) or not isinstance(value, str) or not key.strip() or not value.strip():
        return {'ok': False, 'error': 'Key and value must be nonempty strings.'}
    key, value = key.strip().lower(), value.strip()
    data = load_conventions()
    old = data.get(key)
    if old and old['value'] == value:
        return {'ok': True, 'key': key, 'value': value, 'updated': False}
    now = datetime.now(timezone.utc).isoformat()
    history = list(old.get('history', [])) if old else []
    if old:
        history.append({'value': old['value'], 'updated_at': old.get('updated_at'),
                        'superseded_at': now, 'source': old.get('source', 'user')})
    data[key] = {'value': value, 'updated_at': now, 'source': 'user', 'history': history}
    path = memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as f:
            temporary = f.name
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
    return {'ok': True, 'key': key, 'value': value, 'updated': old is not None}


def render_memory():
    return json.dumps({key: entry['value'] for key, entry in load_conventions().items()},
                      ensure_ascii=False, indent=2)

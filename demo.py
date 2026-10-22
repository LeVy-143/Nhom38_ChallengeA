"""Four real, independent processes; no shared chat history or preseeded memory."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def worker(prompt):
    from main import Agent
    agent = Agent()
    injected = agent.injected_memory
    answer = agent.ask(prompt)
    print(json.dumps({'prompt': prompt, 'injected_memory': json.loads(injected),
                      'answer': answer, 'tools': agent.tool_events}, ensure_ascii=False))


def run():
    with tempfile.TemporaryDirectory() as directory:
        env = dict(os.environ, AGENT_MEMORY_FILE=str(Path(directory) / 'memory.json'))
        prompts = [
            'Ghi nhớ quy ước dự án: authentication dùng JWT. Hãy lưu bằng tool với key authentication, value JWT.',
            'Theo quy ước hiện tại, khi triển khai authentication cho dự án tôi phải dùng gì? Chỉ trả lời tên cơ chế.',
            'Đổi quy ước authentication: bỏ JWT, chuyển sang session cookie. Cập nhật bằng tool với key authentication, value session cookie.',
            'Theo quy ước hiện tại, khi triển khai authentication cho dự án tôi phải dùng gì? Chỉ trả lời tên cơ chế.'
        ]
        results = []
        for index, prompt in enumerate(prompts, 1):
            result = subprocess.run([sys.executable, __file__, '--worker', prompt],
                                    env=env, capture_output=True, text=True, timeout=150)
            if result.returncode:
                raise RuntimeError(f'Session {index} failed; check API access/configuration (stderr hidden to protect credentials).')
            item = json.loads(result.stdout)
            results.append(item)
            print(f'Session {index}: {item["answer"]}', flush=True)
        memory = json.loads(Path(env['AGENT_MEMORY_FILE']).read_text())
        assert results[0]['injected_memory'] == {}
        assert results[1]['injected_memory'] == {'authentication': 'JWT'}
        assert 'jwt' in results[1]['answer'].lower()
        assert results[3]['injected_memory'] == {'authentication': 'session cookie'}
        assert 'session' in results[3]['answer'].lower() and 'cookie' in results[3]['answer'].lower()
        assert 'jwt' not in results[3]['answer'].lower()
        assert memory['authentication']['value'] == 'session cookie'
        assert memory['authentication']['history'][0]['value'] == 'JWT'
        for index in (0, 2):
            assert any(e['tool'] == 'remember_convention' and e['result'].get('ok')
                       for e in results[index]['tools'])
        evidence = {'model': env.get('MODEL_NAME', 'ministral-3b-2512'),
                    'sessions': results, 'final_memory': memory, 'checks': 'PASS'}
        path = Path(__file__).parent / 'artifacts' / 'demo_result.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
        print('PASS: persistence, update, historical value, and actual tool writes. Evidence:', path)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        worker(sys.argv[2])
    else:
        run()

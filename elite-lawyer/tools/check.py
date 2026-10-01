#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精英律师技能包 — 一键体检脚本（V7.6.2 新增；V7.6.6 修跳号与编码并加第 9 项）
用法：
  python3 tools/check.py            # 体检脚本所在技能根
  python3 tools/check.py <skill根>  # 指定其他技能根目录
校验项（共 9 项）：
  1. 四方版本一致性（SKILL frontmatter/标题+blockquote、config.json、README、CHANGELOG）
  2. SKILL.md 版本历史恰 4 条
  3. SKILL.md 文件索引引用的文件真实存在
  4. L0-L3 注册制文件全部登记进 SKILL.md 文件索引
  5. L4 index.md 引用的分片文件存在
  6. JSON 合法性（.state/*.json）
  7. 模块注册表三向校验（L3_模块层/*.md ↔ 模块注册表.md ↔ config.json extensions.modules_registered 逐处对账：漏登与幽灵登记均 FAIL；V7.6.3 建，config 镜像对账为 V7.6.3 维护补丁新增）
  8. 工具痕迹扫描（SENTINEL/PLACEHOLDER/FIXME/待补；演进指南、CHANGELOG、SKILL.md 版本历史与 examples 中的规则记述及模板占位豁免，XXX 类模板写法不算痕迹）
  9. L4 分片反向登记校验（L4 各子目录下的 .md 须逐一登记进 index.md；V7.6.6 新增——固化「模板库/法律意见书.md 漏登索引」同类缺陷的拦截）
退出码：0=全部通过，1=存在 FAIL
"""
import json
import os
import re
import sys

# 控制台编码兜底（V7.6.6）：中文 Windows 的 GBK 控制台无法编码 ✅/❌，
# 直接 print 会 UnicodeEncodeError 崩溃。保留原编码、不可编码字符降级为占位符，
# 既不崩溃也不破坏中文输出（UTF-8 终端下行为不变）。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except Exception:
        pass

FAILS, WARNS, PASSES = [], [], []

def pass_(msg):
    PASSES.append(msg)

def fail(msg):
    FAILS.append(msg)

def warn(msg):
    WARNS.append(msg)

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isfile(os.path.join(root, 'SKILL.md')):
        print(f'[FAIL] 技能根无效：{root} 下无 SKILL.md')
        return 1
    print(f'=== 精英律师技能包体检：{os.path.basename(root.rstrip("/"))} ===')

    sk = read(os.path.join(root, 'SKILL.md'))
    cfg = json.loads(read(os.path.join(root, '.state', 'config.json')))
    rd = read(os.path.join(root, 'README.md'))
    cg = read(os.path.join(root, 'CHANGELOG.md'))

    # ---- 1. 四方版本一致性 ----
    v_fm = (re.search(r'^version:\s*([\d.]+)', sk, re.M) or [None, None])[1]
    v_title = (re.search(r'^# 精英律师数字助手\s+(V[\d.]+)', sk, re.M) or [None, None])[1]
    m_bq = re.search(r'\*\*版本\*\*：(V[\d.]+)', sk)
    v_bq = m_bq.group(1) if m_bq else None
    v_cfg = cfg.get('auto_profile', {}).get('version')
    m_rd = re.search(r'> 版本：(V[\d.]+)', rd)
    v_rd = m_rd.group(1) if m_rd else None
    m_cg = re.search(r'^## (V[\d.]+)', cg, re.M)
    v_cg = m_cg.group(1) if m_cg else None
    versions = {'SKILL.frontmatter': v_fm, 'SKILL.title': v_title, 'SKILL.blockquote': v_bq,
                'config.json': v_cfg, 'README': v_rd, 'CHANGELOG': v_cg}
    normalized = {k: (v or '').lstrip('V') for k, v in versions.items()}
    if len(set(normalized.values())) == 1 and all(normalized.values()):
        pass_(f"四方版本一致：{versions['SKILL.frontmatter']}")
    else:
        fail(f'版本不一致：{versions}')

    # ---- 2. 版本历史恰 4 条 ----
    hist = re.findall(r'^- \*\*V[\d.]+\*\*', sk, re.M)
    if len(hist) == 4:
        pass_('SKILL.md 版本历史恰 4 条')
    else:
        fail(f'SKILL.md 版本历史 {len(hist)} 条（应为 4）')

    # ---- 3. 文件索引引用存在性 ----
    idx_refs = set(re.findall(r'`((?:L[0-4]|\.state|examples)[^`\s]+?\.(?:md|json|py|txt|gitkeep))`', sk))
    missing = sorted(r for r in idx_refs if not os.path.isfile(os.path.join(root, r)))
    if missing:
        fail(f'文件索引引用不存在：{missing}')
    else:
        pass_(f'文件索引引用完整（{len(idx_refs)} 项全部存在）')

    # ---- 4. L0-L3 注册制文件全部登记 ----
    registered = []
    for layer in ['L0_存储层', 'L1_内核层', 'L2_机制层', 'L3_模块层']:
        d = os.path.join(root, layer)
        if os.path.isdir(d):
            registered += [f'{layer}/{f}' for f in os.listdir(d) if f.endswith('.md')]
    unregistered = sorted(f for f in registered if f'`{f}`' not in sk)
    if unregistered:
        fail(f'L0-L3 文件未登记进 SKILL.md 索引：{unregistered}')
    else:
        pass_(f'L0-L3 注册制文件全部登记（{len(registered)} 个）')

    # ---- 5. L4 index 引用存在性 ----
    idx4_path = os.path.join(root, 'L4_知识库层', 'index.md')
    if os.path.isfile(idx4_path):
        idx4 = read(idx4_path)
        refs4 = set(re.findall(r'((?:前沿领域|执业规范|法规库|案例库|模板库|裁判规则|通识库)/[\w\u4e00-\u9fff\-]+\.md)', idx4))
        missing4 = sorted(r for r in refs4 if not os.path.isfile(os.path.join(root, 'L4_知识库层', r)))
        if missing4:
            fail(f'L4 index 引用不存在：{missing4}')
        else:
            pass_(f'L4 index 引用完整（{len(refs4)} 项）')
    else:
        fail('L4_知识库层/index.md 缺失')

    # ---- 6. JSON 合法性 ----
    for f in os.listdir(os.path.join(root, '.state')):
        if f.endswith('.json'):
            try:
                json.loads(read(os.path.join(root, '.state', f)))
                pass_(f'.state/{f} JSON 合法')
            except Exception as e:
                fail(f'.state/{f} JSON 非法：{e}')

    # ---- 7. 模块注册表三向校验（V7.6.3：M14 漏登事故固化） ----
    reg_path = os.path.join(root, 'L0_存储层', '模块注册表.md')
    l3_dir = os.path.join(root, 'L3_模块层')
    if os.path.exists(reg_path):
        reg_refs = set(re.findall(r'L3_模块层/[\w\u4e00-\u9fff\-]+\.md', read(reg_path)))
        actual = {'L3_模块层/' + f for f in os.listdir(l3_dir) if f.endswith('.md')}
        miss = sorted(actual - reg_refs)
        ghost = sorted(reg_refs - actual)
        if miss or ghost:
            fail(f'模块注册表不一致：漏登 {miss or "无"}；幽灵登记 {ghost or "无"}')
        else:
            pass_(f'模块注册表双向一致（{len(actual)} 个模块）')
        # 8b. config.json 镜像对账（V7.6.3 维护补丁：M14 漏扩 config 事故固化——三向对账）
        cfg_path = os.path.join(root, '.state', 'config.json')
        reg_ids = set(re.findall(r'^\| (M\d+) \|', read(reg_path), re.M))
        if os.path.exists(cfg_path):
            cfg_mods = set(json.loads(read(cfg_path)).get('extensions', {}).get('modules_registered', []))
            cfg_miss = sorted(reg_ids - cfg_mods)
            cfg_ghost = sorted(cfg_mods - reg_ids)
            if cfg_miss or cfg_ghost:
                fail(f'config.json modules_registered 与注册表不一致：缺 {cfg_miss or "无"}；多 {cfg_ghost or "无"}')
            else:
                pass_(f'config.json 镜像一致（{len(cfg_mods)} 个模块）')
        else:
            fail('.state/config.json 缺失（模块登记镜像）')
    else:
        fail('L0_存储层/模块注册表.md 缺失')

    # ---- 8. 工具痕迹扫描 ----
    pat = re.compile(r'SENTINEL|PLACEHOLDER|FIXME|待补充?（?此|占位符')
    dirty = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel.startswith('.state') or 'examples' in rel:
            continue
        for f in filenames:
            if not f.endswith('.md'):
                continue
            full = os.path.join(dirpath, f)
            if full in (os.path.join(root, 'L0_存储层', '演进指南.md'), os.path.join(root, 'CHANGELOG.md')):
                continue
            for i, line in enumerate(read(full).splitlines(), 1):
                if f == 'SKILL.md' and line.startswith('## 版本历史'):
                    break  # 版本历史记述审计规则本身（与 CHANGELOG 同理豁免）
                if pat.search(line):
                    dirty.append(f'{os.path.relpath(full, root)}:{i}')
    if dirty:
        warn(f'工具痕迹待人工确认：{dirty[:10]}{"..." if len(dirty) > 10 else ""}')
    else:
        pass_('工具痕迹扫描干净')

    # ---- 9. L4 分片反向登记校验（V7.6.6 新增） ----
    idx_path = os.path.join(root, 'L4_知识库层', 'index.md')
    if os.path.isfile(idx_path):
        idx_text = read(idx_path)
        l4_dirs = ['法规库', '案例库', '模板库', '裁判规则', '执业规范', '前沿领域', '通识库']
        unregistered_l4 = []
        for d in l4_dirs:
            dd = os.path.join(root, 'L4_知识库层', d)
            if not os.path.isdir(dd):
                continue
            for f in sorted(os.listdir(dd)):
                if not f.endswith('.md'):
                    continue
                if f'{d}/{f}' not in idx_text:
                    unregistered_l4.append(f'{d}/{f}')
        if unregistered_l4:
            fail(f'L4 分片未登记进 index.md：{unregistered_l4}')
        else:
            pass_('L4 分片全部登记进 index.md')
    else:
        fail('L4_知识库层/index.md 缺失（反向登记校验无法执行）')

    # ---- 汇总 ----
    print(f'\n[PASS] {len(PASSES)} 项')
    for w in WARNS:
        print(f'[WARN] {w}')
    for f in FAILS:
        print(f'[FAIL] {f}')
    print(f'结论：{"✅ 体检通过" if not FAILS else "❌ 存在 FAIL，禁止发布"}')
    return 0 if not FAILS else 1

if __name__ == '__main__':
    sys.exit(main())

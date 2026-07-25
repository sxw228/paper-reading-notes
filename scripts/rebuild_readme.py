from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = ROOT / "papers"
README_PATH = ROOT / "README.md"
GITHUB_ROOT = "https://github.com/sxw228/paper-reading-notes"
FILENAME_RE = re.compile(r"^(?P<key>[A-Z0-9]{8})-(?P<slug>.+)\.md$")


def markdown_field(text: str, label: str) -> str | None:
    pattern = re.compile(
        rf"^\s*(?:\*\*)?\s*{re.escape(label)}\s*(?:\*\*)?\s*[：:]\s*(?:\*\*)?\s*(.+?)\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    value = re.sub(r"\s*\[pdf:E\d+\]\s*", " ", match.group(1))
    return value.strip().strip("* ").strip()


def clean_cell(value: str | None) -> str:
    if not value:
        return "—"
    return value.replace("|", r"\|").replace("\n", " ").strip()


def normalized_doi(value: str | None) -> str:
    if not value:
        return "—"
    match = re.search(
        r"10\.\d{4,9}/[-._;()/:A-Z0-9]+",
        value,
        re.IGNORECASE,
    )
    if not match:
        return "—"
    return match.group(0).rstrip(".,;，。；")


def load_cards() -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    seen_keys: set[str] = set()

    for path in sorted(PAPERS_DIR.glob("*.md")):
        filename_match = FILENAME_RE.match(path.name)
        if not filename_match:
            raise SystemExit(f"invalid paper filename: {path.name}")

        key = filename_match.group("key")
        if key in seen_keys:
            raise SystemExit(f"duplicate Zotero key in filenames: {key}")
        seen_keys.add(key)

        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
        if not title_match:
            raise SystemExit(f"missing H1 title: {path.name}")

        declared_key = markdown_field(text, "Zotero key")
        declared_key_match = re.search(r"\b[A-Z0-9]{8}\b", declared_key or "")
        if declared_key and (
            not declared_key_match or declared_key_match.group(0) != key
        ):
            raise SystemExit(
                f"Zotero key mismatch: {path.name} declares {declared_key!r}"
            )

        year_value = markdown_field(text, "年份")
        year_match = re.search(r"(?:19|20)\d{2}", year_value or "")
        if not year_match:
            year_match = re.search(
                r"(?:19|20)\d{2}", filename_match.group("slug")
            )
        year = year_match.group(0) if year_match else "—"

        cards.append(
            {
                "key": key,
                "title": title_match.group(1).strip(),
                "year": year,
                "doi": normalized_doi(markdown_field(text, "DOI")),
                "relative_path": path.relative_to(ROOT).as_posix(),
            }
        )

    return sorted(
        cards,
        key=lambda card: (
            -(int(card["year"]) if card["year"].isdigit() else 0),
            card["title"].casefold(),
            card["key"],
        ),
    )


def render_readme(cards: list[dict[str, str]]) -> str:
    lines = [
        "# Paper Reading Notes",
        "",
        "面向 Codex 与 ChatGPT 网页端的论文精读卡仓库。每篇论文对应 `papers/` 下的一份 Markdown；所有卡片属于同一正式语料集合，数量由当前文件自动计算。",
        "",
        "## Agent 访问入口",
        "",
        f"- Codex 本地索引：`{README_PATH}`",
        f"- Codex 本地卡片目录：`{PAPERS_DIR}`",
        f"- ChatGPT 网页端索引：{GITHUB_ROOT}",
        "- 下表中的相对链接在本地解析为 Codex 可读路径，在 GitHub 上解析为 ChatGPT 可打开的网页链接。",
        "- 文献检索先搜索全部卡片正文和 Zotero；这两者都是本地候选发现源，不只是外部结果的查重工具。",
        "- 命中 Zotero key、DOI 或论文身份后，优先完整读取精读卡；只有卡片缺少所需事实或需要核对原文位置时才回到源 PDF。",
        "- 相关性筛选只排除不相关、重复、非论文和身份不明项；不在制卡前替用户判断学术质量。未指定数量时默认形成最相关的 5 篇入围候选。",
        "- 所有入围且无正式精读卡的论文都生成 ChatGPT 网页端 ZIP 与 prompt；缺 PDF 时先加入或复用 Zotero，并等待用户手动取得和挂载。",
        "- 用户交回 reading-result ZIP 即表示同意保留，技术验收通过后直接归档。用户明确不要的论文以 Zotero `reading-card:rejected` 标签持久排除。",
        "",
        "## 检索模式",
        "",
        "- **本地优先（默认）**：只检索本索引、精读卡正文和本地 Zotero，不访问全网；本地证据不足时先报告缺口。",
        "- **免费链路**：先走本地链路，再使用 AnySearch 补充候选。",
        "- **付费链路**：先走本地链路，再使用 AnySearch 与 ai4scholar 补充并交叉核对候选。",
        "- Asta 当前不可用，不属于以上任一模式。",
        "- AnySearch 与 ai4scholar 只负责外部候选发现；外部结果仍需逐篇经过本地精读卡与 Zotero 身份门。",
        "",
        f"## 全部精读卡（{len(cards)}）",
        "",
        "| 年份 | Zotero key | 论文 | DOI |",
        "|---:|---|---|---|",
    ]

    for card in cards:
        lines.append(
            "| {year} | `{key}` | [{title}]({path}) | {doi} |".format(
                year=clean_cell(card["year"]),
                key=card["key"],
                title=clean_cell(card["title"]),
                path=card["relative_path"],
                doi=clean_cell(card["doi"]),
            )
        )

    lines.extend(
        [
            "",
            "## 维护",
            "",
            "新增、删除或重命名卡片后运行：",
            "",
            "```powershell",
            r'python "D:\proj\mac\paper-reading-notes\scripts\rebuild_readme.py"',
            r'python "D:\proj\mac\paper-reading-notes\scripts\rebuild_readme.py" --check',
            "```",
            "",
            "`README.md` 由该脚本生成；不要手工维护论文清单或固定数量。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if README.md is not the generated current index.",
    )
    args = parser.parse_args()

    rendered = render_readme(load_cards())
    if args.check:
        current = README_PATH.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit("README.md is stale; run rebuild_readme.py")
        print(f"README.md is current: {len(load_cards())} cards")
        return 0

    README_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"updated {README_PATH}: {len(load_cards())} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

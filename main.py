import argparse
import sys
from datetime import datetime
from collections import Counter
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.text import Text

# Initialize Rich Console
console = Console()

# ASCII Banner
BANNER = """
 [bold sky_blue]  _____ _ _   _____       _     [/bold sky_blue]
 [bold sky_blue] / ____(_) | |  __ \     | |    [/bold sky_blue]
 [bold sky_blue]| |  __ _| |_| |__) |   _| | ___ ___ [/bold sky_blue]
 [bold sky_blue]| | |_ | | __|  ___/ | | | |/ __/ _ \\[/bold sky_blue]
 [bold sky_blue]| |__| | | |_| |   | |_| | | (_|  __/[/bold sky_blue]
 [bold sky_blue] \_____|_|\__|_|    \__,_|_|\___\___|[/bold sky_blue]
 [bold grey]⚡ GitHub Activity Visualizer & Persona Analyzer[/bold grey]
"""

# MOCK DATA FOR DEMO MODE
MOCK_PROFILE = {
    "login": "ivankafi03",
    "name": "Ivan Kafi Pradana",
    "bio": "Full Stack Developer | Building elegant digital experiences & premium web apps",
    "location": "Indonesia",
    "public_repos": 14,
    "followers": 48,
    "following": 52,
    "created_at": "2021-08-15T08:30:00Z",
}

MOCK_REPOS = [
    {"language": "TypeScript"},
    {"language": "TypeScript"},
    {"language": "JavaScript"},
    {"language": "Python"},
    {"language": "Python"},
    {"language": "TypeScript"},
    {"language": "CSS"},
    {"language": "HTML"},
]

MOCK_EVENTS = [
    {"type": "PushEvent", "created_at": "2026-05-22T23:15:00Z", "payload": {"commits": [{"message": "feat: add dynamic sitemap and robots.txt"}]}},
    {"type": "PushEvent", "created_at": "2026-05-22T22:45:00Z", "payload": {"commits": [{"message": "design: align member login with premium glassmorphism theme"}]}},
    {"type": "PushEvent", "created_at": "2026-05-22T19:20:00Z", "payload": {"commits": [{"message": "fix: resolve pre-hydration logo layout flash"}]}},
    {"type": "PushEvent", "created_at": "2026-05-22T02:10:00Z", "payload": {"commits": [{"message": "refactor: optimize nodemailer transport tls config"}]}},
    {"type": "IssuesEvent", "created_at": "2026-05-21T15:30:00Z", "payload": {"action": "opened"}},
    {"type": "PullRequestEvent", "created_at": "2026-05-20T10:15:00Z", "payload": {"action": "opened"}},
    {"type": "WatchEvent", "created_at": "2026-05-19T14:20:00Z"},
]


def fetch_github_data(username, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    base_url = f"https://api.github.com/users/{username}"
    
    # Fetch Profile
    res_profile = requests.get(base_url, headers=headers)
    if res_profile.status_code == 404:
        console.print(f"[bold red]Error: User '{username}' tidak ditemukan di GitHub![/bold red]")
        sys.exit(1)
    elif res_profile.status_code == 403:
        console.print("[bold yellow]Rate Limit Terlampaui! Menggunakan Mock Mode agar visualisasi tetap berjalan...[/bold yellow]")
        return MOCK_PROFILE, MOCK_REPOS, MOCK_EVENTS, True
    elif res_profile.status_code != 200:
        console.print(f"[bold red]Error: Gagal menghubungi API GitHub ({res_profile.status_code})[/bold red]")
        sys.exit(1)
        
    profile = res_profile.json()
    
    # Fetch Repos (up to 100)
    res_repos = requests.get(f"{base_url}/repos?per_page=100", headers=headers)
    repos = res_repos.json() if res_repos.status_code == 200 else MOCK_REPOS
    
    # Fetch Public Events
    res_events = requests.get(f"{base_url}/events?per_page=100", headers=headers)
    events = res_events.json() if res_events.status_code == 200 else MOCK_EVENTS
    
    return profile, repos, events, False


def generate_statistics(repos, events):
    # 1. Top Languages
    languages = [r["language"] for r in repos if r.get("language")]
    lang_counter = Counter(languages)
    total_langs = sum(lang_counter.values())
    lang_percentages = {lang: (count / total_langs) * 100 for lang, count in lang_counter.items()}
    sorted_langs = sorted(lang_percentages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 2. Activity Counter
    activity_types = [e["type"] for e in events]
    activity_counter = Counter(activity_types)
    
    # 3. Active Hours Analysis
    hours = []
    for e in events:
        try:
            created_at = e["created_at"]
            dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            hours.append(dt.hour)
        except Exception:
            continue
            
    hour_categories = {"Pagi (05-11)": 0, "Siang (11-17)": 0, "Sore (17-22)": 0, "Malam (22-05)": 0}
    for h in hours:
        if 5 <= h < 11:
            hour_categories["Pagi (05-11)"] += 1
        elif 11 <= h < 17:
            hour_categories["Siang (11-17)"] += 1
        elif 17 <= h < 22:
            hour_categories["Sore (17-22)"] += 1
        else:
            hour_categories["Malam (22-05)"] += 1
            
    total_hours = sum(hour_categories.values())
    hour_percentages = {cat: (count / total_hours) * 100 if total_hours > 0 else 0 for cat, count in hour_categories.items()}
    
    return sorted_langs, activity_counter, hour_percentages


def get_developer_persona(activity_counter, hour_percentages):
    # Calculate Night owl percentage
    night_pct = hour_percentages.get("Malam (22-05)", 0)
    morning_pct = hour_percentages.get("Pagi (05-11)", 0)
    
    commits = activity_counter.get("PushEvent", 0)
    prs = activity_counter.get("PullRequestEvent", 0)
    issues = activity_counter.get("IssuesEvent", 0)
    reviews = activity_counter.get("PullRequestReviewEvent", 0)
    
    # Determine Status
    if night_pct > 40:
        status = "Night Owl 🦉 (Kelelawar Malam)"
        persona = "Anda adalah pelindung kode di kegelapan malam. Saat dunia terlelap, jari-jemari Anda menari lincah merilis baris kode premium berkualitas tinggi."
    elif morning_pct > 40:
        status = "Early Bird 🌅 (Burung Pagi)"
        persona = "Anda berenergi tinggi saat fajar menyingsing. Kopi pagi dan commit pertama Anda adalah sinergi sempurna untuk memulai produktivitas tim."
    elif commits > 15:
        status = "Commit Machine 🚀 (Mesin Git)"
        persona = "Frekuensi push Anda sangat luar biasa! Anda tidak membiarkan perubahan kecil menumpuk tanpa dikomit secara berkala. Git push adalah hidup Anda."
    elif prs > 5 or reviews > 5:
        status = "Team Collaborator 🤝 (Pemain Tim)"
        persona = "Fokus Anda adalah kolaborasi. Anda gemar mengulas kode rekan tim, menyetujui Pull Request, dan menjaga kualitas integrasi tetap kokoh."
    elif issues > 5:
        status = "Problem Solver 🛠️ (Pemecah Masalah)"
        persona = "Anda adalah seorang detektif bug! Anda gemar membuka isu, melacak bug yang membandel, dan menyusun peta jalan perbaikan sistem secara rapi."
    else:
        status = "Focused Craftsman 💎 (Pengrajin Kode)"
        persona = "Anda bekerja secara tenang dan terfokus. Setiap commit Anda dipikirkan dengan matang, menghasilkan kontribusi yang elegan dan minim bug."
        
    return status, persona


def render_tui(profile, sorted_langs, activity_counter, hour_percentages, status, persona, is_mock):
    # Header Banner
    console.print(Align.center(BANNER))
    if is_mock:
        console.print(Align.center("[bold yellow][DEMO MODE - MOCK DATA][/bold yellow]\n"))
    
    # Profile Panel (Left)
    profile_text = Text()
    profile_text.append(f"👤 Nama: ", style="bold sky_blue")
    profile_text.append(f"{profile.get('name') or 'N/A'}\n")
    profile_text.append(f"🔗 Username: ", style="bold sky_blue")
    profile_text.append(f"@{profile.get('login')}\n")
    profile_text.append(f"📍 Lokasi: ", style="bold sky_blue")
    profile_text.append(f"{profile.get('location') or 'N/A'}\n")
    profile_text.append(f"📝 Bio: ", style="bold sky_blue")
    profile_text.append(f"{profile.get('bio') or 'No Bio'}\n\n")
    profile_text.append(f"👥 Followers: ", style="bold green")
    profile_text.append(f"{profile.get('followers')}   ")
    profile_text.append(f"🤝 Following: ", style="bold green")
    profile_text.append(f"{profile.get('following')}\n")
    profile_text.append(f"📂 Repositori Publik: ", style="bold green")
    profile_text.append(f"{profile.get('public_repos')}")
    
    profile_panel = Panel(
        profile_text,
        title="[bold white]👤 Ringkasan Profil[/bold white]",
        border_style="sky_blue",
        height=12
    )
    
    # Languages & Active Hours Panel (Right)
    right_text = Text()
    
    # Languages Bar Chart
    right_text.append("📊 Bahasa Pemrograman Favorit:\n", style="bold white")
    for lang, pct in sorted_langs:
        bar_len = int(pct / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        right_text.append(f"  {lang:<12} {bar} {pct:.1f}%\n", style="sky_blue")
        
    # Active Hours Bar Chart
    right_text.append("\n🕒 Pola Jam Coding (Waktu Aktif):\n", style="bold white")
    for cat, pct in hour_percentages.items():
        bar_len = int(pct / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        right_text.append(f"  {cat:<14} {bar} {pct:.1f}%\n", style="indigo")
        
    stats_panel = Panel(
        right_text,
        title="[bold white]📈 Analitik Pengkodean[/bold white]",
        border_style="indigo",
        height=12
    )
    
    # Print Twin Columns
    console.print(Columns([profile_panel, stats_panel], expand=True))
    console.print()
    
    # Activity Breakdown Table
    table = Table(title="[bold white]🔔 100 Aktivitas Terakhir di GitHub[/bold white]", border_style="grey37", expand=True)
    table.add_column("Jenis Event", style="bold sky_blue", width=25)
    table.add_column("Jumlah Kejadian", style="bold green", justify="center")
    table.add_column("Deskripsi Aktivitas", style="grey70")
    
    event_descriptions = {
        "PushEvent": "Melakukan push commit baru ke repositori",
        "PullRequestEvent": "Membuka atau menggabungkan (merge) Pull Request",
        "IssuesEvent": "Membuat, menutup, atau mengomentari Isu bug/tugas",
        "WatchEvent": "Memberikan bintang (star) pada repositori orang lain",
        "CreateEvent": "Membuat repositori atau branch baru",
        "IssueCommentEvent": "Menulis komentar pada laporan isu",
        "PullRequestReviewEvent": "Mengulas (review) kode tim pada PR",
    }
    
    for ev_type, count in activity_counter.items():
        desc = event_descriptions.get(ev_type, "Aktivitas interaksi GitHub lainnya")
        table.add_row(ev_type, str(count), desc)
        
    if not activity_counter:
        table.add_row("No Recent Activity", "0", "Belum ada aktivitas publik terekam dalam beberapa hari ini.")
        
    console.print(table)
    console.print()
    
    # Developer Persona Panel (Bottom)
    persona_text = Text()
    persona_text.append(f"🏆 Status Developer: ", style="bold sky_blue")
    persona_text.append(f"{status}\n\n", style="bold yellow")
    persona_text.append(f"🧠 Deskripsi Karakter:\n", style="bold white")
    persona_text.append(f"\"{persona}\"", style="italic grey78")
    
    persona_panel = Panel(
        persona_text,
        title="[bold white]🧠 Analisis Kepribadian Developer (AI Persona)[/bold white]",
        border_style="yellow",
        padding=(1, 2)
    )
    console.print(persona_panel)
    console.print()


def export_markdown_report(username, profile, sorted_langs, hour_percentages, status, persona):
    filename = f"{username}_gitpulse_report.md"
    
    report_content = f"""# ⚡ GitPulse Report - @{username}
Laporan Analitik Aktivitas GitHub Otomatis yang Dihasilkan pada {datetime.now().strftime('%d-%m-%Y %H:%M')}.

---

## 👤 Ringkasan Profil
- **Nama Lengkap:** {profile.get('name') or 'N/A'}
- **Lokasi:** {profile.get('location') or 'N/A'}
- **Bio:** {profile.get('bio') or 'No bio provided'}
- **Followers / Following:** {profile.get('followers')} / {profile.get('following')}
- **Repositori Publik:** {profile.get('public_repos')}

---

## 📊 Bahasa Pemrograman Favorit
| Bahasa | Persentase Kontribusi |
| :--- | :---: |
"""
    for lang, pct in sorted_langs:
        report_content += f"| {lang} | {pct:.1f}% |\n"
        
    report_content += """
---

## 🕒 Pola Waktu Coding
| Kategori Waktu | Persentase Aktivitas |
| :--- | :---: |
"""
    for cat, pct in hour_percentages.items():
        report_content += f"| {cat} | {pct:.1f}% |\n"
        
    report_content += f"""
---

## 🧠 Analisis Kepribadian Developer (AI Persona)
- **Status Developer:** **{status}**
- **Deskripsi Karakter:**  
  *"{persona}"*

---
*Dibuat dengan penuh cinta menggunakan **GitPulse CLI Tool** ⚡*
"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    console.print(f"[bold green]✨ Laporan PDF/Markdown sukses diekspor ke: [underline]{filename}[/underline][/bold green]\n")


def main():
    parser = argparse.ArgumentParser(description="GitPulse - GitHub Activity Visualizer & Persona Analyzer")
    parser.add_argument("-u", "--username", type=str, help="Username GitHub yang ingin dianalisis")
    parser.add_argument("-t", "--token", type=str, help="GitHub Personal Access Token (opsional, untuk menghindari rate limit)")
    parser.add_argument("-m", "--mock", action="store_true", help="Gunakan Demo Mock Data untuk uji coba instan")
    
    args = parser.parse_args()
    
    if args.mock or not args.username:
        if not args.username and not args.mock:
            console.print("[bold yellow]Peringatan: Username tidak dicantumkan. Beralih otomatis ke MOCK DEMO MODE...[/bold yellow]\n")
        profile, repos, events, is_mock = MOCK_PROFILE, MOCK_REPOS, MOCK_EVENTS, True
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task(description="Menghubungi API GitHub dan menarik data...", total=None)
            profile, repos, events, is_mock = fetch_github_data(args.username, args.token)
            
    # Process Stats
    sorted_langs, activity_counter, hour_percentages = generate_statistics(repos, events)
    
    # Process Persona
    status, persona = get_developer_persona(activity_counter, hour_percentages)
    
    # Render Dashboard
    render_tui(profile, sorted_langs, activity_counter, hour_percentages, status, persona, is_mock)
    
    # Export Report
    export_markdown_report(profile["login"], profile, sorted_langs, hour_percentages, status, persona)


if __name__ == "__main__":
    main()

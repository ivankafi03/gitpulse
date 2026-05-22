import argparse
import sys
import re
from datetime import datetime, date, timedelta
from collections import Counter
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt
from rich import box

# Ensure standard output supports UTF-8, especially on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialize Rich Console
console = Console()

# ASCII Banner (Emoji-Free, Indonesian Subtitle)
BANNER = r"""
 [bold cyan]  _____ _ _   _____       _     [/bold cyan]
 [bold cyan] / ____(_) | |  __ \     | |    [/bold cyan]
 [bold cyan]| |  __ _| |_| |__) |   _| | ___ ___ [/bold cyan]
 [bold cyan]| | |_ | | __|  ___/ | | | |/ __/ _ \\[/bold cyan]
 [bold cyan]| |__| | | |_| |   | |_| | | (_|  __/[/bold cyan]
 [bold cyan] \_____|_|\__|_|    \__,_|_|\___\___|[/bold cyan]
 [bold grey]GITPULSE - Analitik Aktivitas & Karakter Developer GitHub[/bold grey]
"""

# MOCK DATA FOR DEMO MODE (User A)
MOCK_PROFILE = {
    "login": "dev_pratama",
    "name": "Developer Pratama",
    "bio": "Full Stack Developer | Building elegant digital experiences & premium web apps",
    "location": "Indonesia",
    "public_repos": 14,
    "followers": 48,
    "following": 52,
    "created_at": "2021-08-15T08:30:00Z",
}

# Distribute mock events over recent weeks to show a beautiful grid pattern
MOCK_EVENTS = []
base_time = datetime.now()
# We add a variety of commits on different days to make the grid look beautiful
commit_offsets = [0, 1, 2, 4, 7, 8, 9, 14, 15, 16, 21, 22, 28, 35, 42, 49, 50, 56, 63, 70, 77, 84, 91, 105, 112, 119]
for idx, offset in enumerate(commit_offsets):
    event_time = base_time - timedelta(days=offset, hours=idx % 4 + 10)
    event_str = event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Add multiple events on some days
    count = 3 if idx % 5 == 0 else (1 if idx % 2 == 0 else 2)
    for _ in range(count):
        MOCK_EVENTS.append({
            "type": "PushEvent",
            "created_at": event_str,
            "payload": {"commits": [{"message": f"feat: update profile and scripts offset {offset}"}]}
        })

# Other events for breakdown
MOCK_EVENTS.append({"type": "IssuesEvent", "created_at": (base_time - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ"), "payload": {"action": "opened"}})
MOCK_EVENTS.append({"type": "PullRequestEvent", "created_at": (base_time - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"), "payload": {"action": "opened"}})
MOCK_EVENTS.append({"type": "WatchEvent", "created_at": (base_time - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")})

MOCK_REPOS = [
    {"name": "undangan-digital", "language": "TypeScript", "stargazers_count": 12, "forks_count": 4, "pushed_at": "2026-05-22T19:20:00Z"},
    {"name": "fikadigi-store", "language": "TypeScript", "stargazers_count": 8, "forks_count": 2, "pushed_at": "2026-05-20T10:00:00Z"},
    {"name": "gitpulse", "language": "Python", "stargazers_count": 5, "forks_count": 1, "pushed_at": "2026-05-22T20:00:00Z"},
    {"name": "python-basics", "language": "Python", "stargazers_count": 2, "forks_count": 0, "pushed_at": "2025-11-15T08:30:00Z"},
    {"name": "simple-portfolio", "language": "HTML", "stargazers_count": 1, "forks_count": 0, "pushed_at": "2024-05-01T12:00:00Z"},
]

# MOCK DATA FOR USER B (rivaldi01) - For Compare Mode Offline Demo
MOCK_PROFILE_B = {
    "login": "rivaldi01",
    "name": "Rivaldi Suryanegara",
    "bio": "Backend Engineer | Go & Python enthusiast | Cloud Architect",
    "location": "Bandung, Indonesia",
    "public_repos": 22,
    "followers": 75,
    "following": 40,
    "created_at": "2020-04-12T10:15:00Z",
}

MOCK_REPOS_B = [
    {"name": "go-grpc-microservice", "language": "Go", "stargazers_count": 42, "forks_count": 12, "pushed_at": "2026-05-20T12:00:00Z"},
    {"name": "python-data-pipeline", "language": "Python", "stargazers_count": 15, "forks_count": 5, "pushed_at": "2026-05-18T10:00:00Z"},
    {"name": "kubernetes-configs", "language": "Shell", "stargazers_count": 8, "forks_count": 2, "pushed_at": "2026-05-10T08:00:00Z"},
    {"name": "redis-caching-layer", "language": "Go", "stargazers_count": 5, "forks_count": 1, "pushed_at": "2025-12-15T15:00:00Z"},
]

MOCK_EVENTS_B = []
for idx, offset in enumerate(commit_offsets):
    event_time = base_time - timedelta(days=offset + 2, hours=idx % 3 + 9)
    event_str = event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    MOCK_EVENTS_B.append({
        "type": "PushEvent",
        "created_at": event_str,
        "payload": {"commits": [{"message": f"feat: backend pipeline updates offset {offset}"}]}
    })


def strip_rich_tags(text):
    return re.sub(r'\[/?.*?\]', '', text)


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
    languages = [r["language"] for r in repos if isinstance(r, dict) and r.get("language")]
    lang_counter = Counter(languages)
    total_langs = sum(lang_counter.values())
    lang_percentages = {lang: (count / total_langs) * 100 for lang, count in lang_counter.items()} if total_langs > 0 else {}
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
    hour_percentages = {cat: (count / total_hours) * 100 if total_hours > 0 else 0.0 for cat, count in hour_categories.items()}
    
    # 4. Weekly Rhythm Analysis
    weekdays = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    weekday_counts = {day: 0 for day in weekdays}
    for e in events:
        try:
            created_at = e.get("created_at")
            if not created_at:
                continue
            dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            day_name = weekdays[dt.weekday()]
            weekday_counts[day_name] += 1
        except Exception:
            continue
    total_days_activity = sum(weekday_counts.values())
    weekday_percentages = {day: (count, (count / total_days_activity) * 100 if total_days_activity > 0 else 0.0) for day, count in weekday_counts.items()}
    
    # 5. Top Repositories with custom status
    valid_repos = []
    for r in repos:
        if isinstance(r, dict) and "name" in r:
            valid_repos.append(r)
            
    # Sort repos by stars, forks, size
    sorted_repos = sorted(
        valid_repos,
        key=lambda x: (x.get("stargazers_count", 0), x.get("forks_count", 0), x.get("size", 0)),
        reverse=True
    )[:5] # Display top 5 in table
    
    # Add activity status to repos
    for r in sorted_repos:
        pushed_at_str = r.get("pushed_at") or r.get("updated_at")
        repo_status = "Stabil"
        if pushed_at_str:
            try:
                push_yr = int(pushed_at_str[:4])
                if push_yr >= 2026:
                    repo_status = "Sangat Aktif"
                elif push_yr >= 2025:
                    repo_status = "Aktif"
                else:
                    repo_status = "Arsip"
            except Exception:
                pass
        r["activity_status"] = repo_status
    
    return sorted_langs, activity_counter, hour_percentages, weekday_percentages, sorted_repos


def generate_contribution_grid(events):
    today = date.today()
    num_weeks = 20
    
    # Calculate starting date aligned to Sunday 20 weeks ago, including current week in the last column
    days_since_sunday = (today.weekday() + 1) % 7
    current_week_sunday = today - timedelta(days=days_since_sunday)
    start_date = current_week_sunday - timedelta(weeks=num_weeks - 1)
    
    grid = [[0 for _ in range(num_weeks)] for _ in range(7)]
    
    # Parse event dates and count contributions
    for e in events:
        try:
            created_at_str = e.get("created_at")
            if not created_at_str:
                continue
            event_dt = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").date()
            diff_days = (event_dt - start_date).days
            if diff_days >= 0:
                col = diff_days // 7
                row = diff_days % 7
                if 0 <= col < num_weeks and 0 <= row < 7:
                    grid[row][col] += 1
        except Exception:
            continue
            
    # Visual String Generation
    weekdays_labels = ["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]
    indonesian_months = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
        7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
    }
    
    month_labels = [" " * 6]
    last_month = None
    for col in range(num_weeks):
        col_date = start_date + timedelta(days=col * 7)
        month_name = indonesian_months[col_date.month]
        if month_name != last_month:
            current_len = len("".join(month_labels))
            target_pos = 6 + col * 2
            if target_pos > current_len:
                month_labels.append(" " * (target_pos - current_len))
            month_labels.append(month_name)
            last_month = month_name
            
    month_row = "".join(month_labels)[:num_weeks * 2 + 6]
    
    grid_rows = []
    for r in range(7):
        row_str = f"  {weekdays_labels[r]:<4} "
        for c in range(num_weeks):
            count = grid[r][c]
            if count == 0:
                row_str += "[grey37]░[/grey37] "
            elif count <= 2:
                row_str += "[cyan]▒[/cyan] "
            elif count <= 5:
                row_str += "[bold cyan]▓[/bold cyan] "
            else:
                row_str += "[bold white]█[/bold white] "
        grid_rows.append(row_str)
        
    # Calculate summary statistics for daily and weekly activity
    total_contributions = sum(sum(row) for row in grid)
    rata_mingguan = total_contributions / num_weeks
    rata_harian = total_contributions / (num_weeks * 7)
    
    weekdays_full = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    row_sums = [sum(grid[r]) for r in range(7)]
    max_row_idx = row_sums.index(max(row_sums)) if total_contributions > 0 else 0
    hari_teraktif_nama = weekdays_full[max_row_idx] if total_contributions > 0 else "N/A"
    hari_teraktif_count = row_sums[max_row_idx] if total_contributions > 0 else 0
    
    summary_stats = {
        "total": total_contributions,
        "rata_mingguan": rata_mingguan,
        "rata_harian": rata_harian,
        "hari_teraktif": hari_teraktif_nama,
        "hari_teraktif_count": hari_teraktif_count
    }
    
    return month_row, grid_rows, summary_stats


def get_developer_persona(activity_counter, hour_percentages):
    night_pct = hour_percentages.get("Malam (22-05)", 0)
    morning_pct = hour_percentages.get("Pagi (05-11)", 0)
    
    commits = activity_counter.get("PushEvent", 0)
    prs = activity_counter.get("PullRequestEvent", 0)
    issues = activity_counter.get("IssuesEvent", 0)
    reviews = activity_counter.get("PullRequestReviewEvent", 0)
    
    # Determine Status
    if night_pct > 40:
        status = "Night Owl (Kelelawar Malam)"
        persona = "Anda adalah pelindung kode di kegelapan malam. Saat dunia terlelap, jari-jemari Anda menari lincah merilis baris kode premium berkualitas tinggi."
    elif morning_pct > 40:
        status = "Early Bird (Burung Pagi)"
        persona = "Anda berenergi tinggi saat fajar menyingsing. Kopi pagi dan commit pertama Anda adalah sinergi sempurna untuk memulai produktivitas tim."
    elif commits > 15:
        status = "Commit Machine (Mesin Git)"
        persona = "Frekuensi push Anda sangat luar biasa! Anda tidak membiarkan perubahan kecil menumpuk tanpa dikomit secara berkala. Git push adalah hidup Anda."
    elif prs > 5 or reviews > 5:
        status = "Team Collaborator (Pemain Tim)"
        persona = "Fokus Anda adalah kolaborasi. Anda gemar mengulas kode rekan tim, menyetujui Pull Request, dan menjaga kualitas integrasi tetap kokoh."
    elif issues > 5:
        status = "Problem Solver (Pemecah Masalah)"
        persona = "Anda adalah seorang detektif bug! Anda gemar membuka isu, melacak bug yang membandel, dan menyusun peta jalan perbaikan sistem secara rapi."
    else:
        status = "Focused Craftsman (Pengrajin Kode)"
        persona = "Anda bekerja secara tenang dan terfokus. Setiap commit Anda dipikirkan dengan matang, menghasilkan kontribusi yang elegan dan minim bug."
        
    return status, persona


def render_tui(profile, sorted_langs, activity_counter, hour_percentages, weekday_percentages, sorted_repos, status, persona, is_mock, events):
    # Header Banner
    console.print(Align.center(BANNER))
    if is_mock:
        console.print(Align.center("[bold yellow][MODE DEMO - DATA MOCK][/bold yellow]\n"))
    
    # Row 1: Profile Panel (Left)
    profile_text = Text()
    profile_text.append("Nama Lengkap : ", style="bold cyan")
    profile_text.append(f"{profile.get('name') or 'N/A'}\n")
    profile_text.append("Username     : ", style="bold cyan")
    profile_text.append(f"@{profile.get('login')}\n")
    profile_text.append("Lokasi       : ", style="bold cyan")
    profile_text.append(f"{profile.get('location') or 'N/A'}\n")
    profile_text.append("Bio          : ", style="bold cyan")
    
    bio = profile.get('bio') or 'Tidak ada bio.'
    if len(bio) > 80:
        bio = bio[:77] + "..."
    profile_text.append(f"{bio}\n\n")
    
    profile_text.append("Pengikut (Followers) : ", style="bold white")
    profile_text.append(f"{profile.get('followers')}   ", style="cyan")
    profile_text.append("Mengikuti (Following): ", style="bold white")
    profile_text.append(f"{profile.get('following')}\n", style="cyan")
    profile_text.append("Repositori Publik    : ", style="bold white")
    profile_text.append(f"{profile.get('public_repos')}\n", style="cyan")
    
    profile_panel = Panel(
        profile_text,
        title="[bold white]Ringkasan Profil[/bold white]",
        border_style="cyan",
        box=box.ROUNDED,
        height=12
    )
    
    # Row 1: Coding Analytics Panel (Right)
    right_text = Text()
    
    # Languages Bar Chart
    right_text.append("Bahasa Pemrograman Teratas:\n", style="bold white")
    if sorted_langs:
        for lang, pct in sorted_langs[:3]:
            bar_len = int(pct / 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            right_text.append(f"  {lang:<12} {bar} {pct:.1f}%\n", style="cyan")
    else:
        right_text.append("  Tidak ada data bahasa.\n", style="grey70")
        
    # Active Hours Bar Chart
    right_text.append("\nPola Waktu Kontribusi:\n", style="bold white")
    for cat, pct in hour_percentages.items():
        bar_len = int(pct / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        right_text.append(f"  {cat:<14} {bar} {pct:.1f}%\n", style="magenta")
        
    stats_panel = Panel(
        right_text,
        title="[bold white]Analitik Bahasa & Waktu[/bold white]",
        border_style="magenta",
        box=box.ROUNDED,
        height=12
    )
    
    # Print Row 1
    console.print(Columns([profile_panel, stats_panel], expand=True))
    console.print()
    
    # Row 2: Weekly Rhythm Panel (Left)
    weekly_text = Text()
    weekly_text.append("Ritme Aktivitas Harian (Senin - Minggu):\n", style="bold white")
    for day, (count, pct) in weekday_percentages.items():
        bar_len = int(pct / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        weekly_text.append(f"  {day:<8} {bar} {count:>3} kontribusi ({pct:.1f}%)\n", style="green")
        
    weekly_panel = Panel(
        weekly_text,
        title="[bold white]Ritme Aktivitas Mingguan[/bold white]",
        border_style="green",
        box=box.ROUNDED,
        height=12
    )
    
    # Row 2: Character & Persona Panel (Right)
    persona_text = Text()
    persona_text.append("Status Karakter: ", style="bold white")
    persona_text.append(f"{status}\n\n", style="bold yellow")
    persona_text.append("Analisis Karakter:\n", style="bold white")
    persona_text.append(f"\"{persona}\"", style="italic grey78")
    
    persona_panel = Panel(
        persona_text,
        title="[bold white]Analisis Karakter Developer[/bold white]",
        border_style="yellow",
        box=box.ROUNDED,
        height=12
    )
    
    # Print Row 2
    console.print(Columns([weekly_panel, persona_panel], expand=True))
    console.print()
    
    # Row 3: Contribution Calendar Grid Panel (Full Width)
    month_row, grid_rows, summary_stats = generate_contribution_grid(events)
    grid_text = Text()
    grid_text.append(f"{month_row}\n", style="bold white")
    for r in grid_rows:
        grid_text.append(Text.from_markup(f"{r}\n"))
    legend = "\n      Skala Kontribusi: [grey37]░[/grey37] 0 | [cyan]▒[/cyan] 1-2 | [bold cyan]▓[/bold cyan] 3-5 | [bold white]█[/bold white] 6+"
    grid_text.append(Text.from_markup(legend))
    
    # Add beautiful summary statistics text inside the panel
    stats_summary = f"\n\n      Ringkasan Kontribusi: Total {summary_stats['total']} kontribusi | Rata-rata Mingguan: {summary_stats['rata_mingguan']:.1f} | Rata-rata Harian: {summary_stats['rata_harian']:.2f} | Hari Teraktif: {summary_stats['hari_teraktif']} ({summary_stats['hari_teraktif_count']} kontribusi)"
    grid_text.append(Text.from_markup(f"[bold cyan]{stats_summary}[/bold cyan]"))
    
    grid_panel = Panel(
        grid_text,
        title="[bold white]Kalender Kontribusi GitHub (20 Minggu Terakhir)[/bold white]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(grid_panel)
    console.print()
    
    # Row 4: Top Repositories Insights Table
    repo_table = Table(title="[bold white]Repositori Terpopuler & Analisis Keaktifan[/bold white]", border_style="cyan", box=box.ROUNDED, expand=True)
    repo_table.add_column("Nama Repositori", style="bold cyan", width=30)
    repo_table.add_column("Bahasa Utama", style="bold white", justify="center")
    repo_table.add_column("Bintang (Stars)", style="bold yellow", justify="center")
    repo_table.add_column("Fork", style="bold magenta", justify="center")
    repo_table.add_column("Status Keaktifan", style="bold green", justify="center")
    
    for r in sorted_repos:
        status_color = "green" if r["activity_status"] == "Sangat Aktif" else ("cyan" if r["activity_status"] == "Aktif" else "grey70")
        repo_table.add_row(
            r.get("name"),
            r.get("language") or "N/A",
            str(r.get("stargazers_count", 0)),
            str(r.get("forks_count", 0)),
            f"[{status_color}]{r['activity_status']}[/{status_color}]"
        )
        
    if not sorted_repos:
        repo_table.add_row("Tidak ada repositori ditemukan", "N/A", "0", "0", "[grey70]Stabil[/grey70]")
        
    console.print(repo_table)
    console.print()
    
    # Row 5: Activity Breakdown Table
    table = Table(title="[bold white]Distribusi 100 Aktivitas Terakhir di GitHub[/bold white]", border_style="grey37", box=box.ROUNDED, expand=True)
    table.add_column("Jenis Event", style="bold cyan", width=25)
    table.add_column("Jumlah Kejadian", style="bold green", justify="center")
    table.add_column("Deskripsi Aktivitas", style="grey70")
    
    event_descriptions = {
        "PushEvent": "Melakukan push commit baru ke repositori",
        "PullRequestEvent": "Membuka atau menggabungkan (merge) Pull Request",
        "IssuesEvent": "Membuat, menutup, atau mengomentari Isu bug/tugas",
        "WatchEvent": "Memberikan bintang (star) pada repositori",
        "CreateEvent": "Membuat repositori atau branch baru",
        "IssueCommentEvent": "Menulis komentar pada laporan isu",
        "PullRequestReviewEvent": "Mengulas (review) kode tim pada PR",
    }
    
    for ev_type, count in activity_counter.items():
        desc = event_descriptions.get(ev_type, "Aktivitas interaksi GitHub lainnya")
        table.add_row(ev_type, str(count), desc)
        
    if not activity_counter:
        table.add_row("Tidak Ada Aktivitas", "0", "Belum ada aktivitas publik terekam dalam periode ini.")
        
    console.print(table)
    console.print()


def render_comparison_tui(userA, statsA, userB, statsB, is_mock):
    profileA, reposA, eventsA = statsA["profile"], statsA["repos"], statsA["events"]
    profileB, reposB, eventsB = statsB["profile"], statsB["repos"], statsB["events"]
    
    # Calculate stats for A
    langsA, actA, hourA, weekA, repos_listA = generate_statistics(reposA, eventsA)
    statusA, personaA = get_developer_persona(actA, hourA)
    starsA = sum(r.get("stargazers_count", 0) for r in reposA if isinstance(r, dict))
    forksA = sum(r.get("forks_count", 0) for r in reposA if isinstance(r, dict))
    top_langA = langsA[0][0] if langsA else "N/A"
    active_hourA = sorted(hourA.items(), key=lambda x: x[1], reverse=True)[0][0] if hourA else "N/A"
    
    # Calculate stats for B
    langsB, actB, hourB, weekB, repos_listB = generate_statistics(reposB, eventsB)
    statusB, personaB = get_developer_persona(actB, hourB)
    starsB = sum(r.get("stargazers_count", 0) for r in reposB if isinstance(r, dict))
    forksB = sum(r.get("forks_count", 0) for r in reposB if isinstance(r, dict))
    top_langB = langsB[0][0] if langsB else "N/A"
    active_hourB = sorted(hourB.items(), key=lambda x: x[1], reverse=True)[0][0] if hourB else "N/A"
    
    console.print(Align.center(BANNER))
    console.print(Align.center(f"[bold cyan]PERBANDINGAN DEVELOPER: @{userA} vs @{userB}[/bold cyan]"))
    if is_mock:
        console.print(Align.center("[bold yellow][MODE DEMO - DATA MOCK][/bold yellow]"))
    console.print()
    
    # Comparison Table
    table = Table(border_style="cyan", box=box.ROUNDED, expand=True)
    table.add_column("Metrik Analisis", style="bold white", width=25)
    table.add_column(f"@{userA}", style="bold cyan", justify="center")
    table.add_column(f"@{userB}", style="bold magenta", justify="center")
    
    def format_row(valA, valB, type_val="str"):
        if type_val == "int":
            intA, intB = int(valA), int(valB)
            if intA > intB:
                return f"[bold green]{valA}[/bold green]", str(valB)
            elif intB > intA:
                return str(valA), f"[bold green]{valB}[/bold green]"
            else:
                return str(valA), str(valB)
        else:
            return str(valA), str(valB)
            
    row_nameA, row_nameB = format_row(profileA.get("name") or "N/A", profileB.get("name") or "N/A")
    table.add_row("Nama Lengkap", row_nameA, row_nameB)
    
    row_reposA, row_reposB = format_row(profileA.get("public_repos", 0), profileB.get("public_repos", 0), "int")
    table.add_row("Repositori Publik", row_reposA, row_reposB)
    
    row_follA, row_follB = format_row(profileA.get("followers", 0), profileB.get("followers", 0), "int")
    table.add_row("Pengikut (Followers)", row_follA, row_follB)
    
    table.add_row("Bahasa Utama", top_langA, top_langB)
    table.add_row("Jam Coding Aktif", active_hourA, active_hourB)
    table.add_row("Status Karakter", statusA, statusB)
    
    row_starsA, row_starsB = format_row(starsA, starsB, "int")
    table.add_row("Total Bintang (Stars)", row_starsA, row_starsB)
    
    row_forksA, row_forksB = format_row(forksA, forksB, "int")
    table.add_row("Total Fork", row_forksA, row_forksB)
    
    console.print(table)
    console.print()
    
    # Verdict Panel
    scoreA = (1 if profileA.get("public_repos", 0) > profileB.get("public_repos", 0) else 0) + \
             (1 if profileA.get("followers", 0) > profileB.get("followers", 0) else 0) + \
             (1 if starsA > starsB else 0)
    scoreB = (1 if profileB.get("public_repos", 0) > profileA.get("public_repos", 0) else 0) + \
             (1 if profileB.get("followers", 0) > profileA.get("followers", 0) else 0) + \
             (1 if starsB > starsA else 0)
             
    if scoreA > scoreB:
        verdict = f"@{userA} memiliki pengaruh repositori dan jejak sosial yang lebih kuat di GitHub berdasarkan metrik saat ini."
    elif scoreB > scoreA:
        verdict = f"@{userB} memimpin perbandingan statistik dengan keunggulan pada kontribusi publik dan keterlibatan komunitas."
    else:
        verdict = "Kedua developer memiliki kekuatan yang seimbang dengan keunikan profil coding masing-masing!"
        
    verdict_text = Text()
    verdict_text.append("Analisis Perbandingan:\n", style="bold white")
    verdict_text.append(f"@{userA} diklasifikasikan sebagai ", style="cyan")
    verdict_text.append(f"{statusA}", style="bold yellow")
    verdict_text.append(" sementara ", style="white")
    verdict_text.append(f"@{userB} ", style="magenta")
    verdict_text.append("diklasifikasikan sebagai ", style="white")
    verdict_text.append(f"{statusB}.\n\n", style="bold yellow")
    verdict_text.append(verdict, style="italic white")
    
    verdict_panel = Panel(
        verdict_text,
        title="[bold white]Keputusan Analisis Komparatif[/bold white]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(verdict_panel)
    console.print()


def export_comparison_report(userA, statsA, userB, statsB):
    filename = f"{userA}_vs_{userB}_comparison_report.md"
    
    profileA, reposA, eventsA = statsA["profile"], statsA["repos"], statsA["events"]
    profileB, reposB, eventsB = statsB["profile"], statsB["repos"], statsB["events"]
    
    langsA, actA, hourA, weekA, repos_listA = generate_statistics(reposA, eventsA)
    statusA, _ = get_developer_persona(actA, hourA)
    starsA = sum(r.get("stargazers_count", 0) for r in reposA if isinstance(r, dict))
    forksA = sum(r.get("forks_count", 0) for r in reposA if isinstance(r, dict))
    top_langA = langsA[0][0] if langsA else "N/A"
    active_hourA = sorted(hourA.items(), key=lambda x: x[1], reverse=True)[0][0] if hourA else "N/A"
    
    langsB, actB, hourB, weekB, repos_listB = generate_statistics(reposB, eventsB)
    statusB, _ = get_developer_persona(actB, hourB)
    starsB = sum(r.get("stargazers_count", 0) for r in reposB if isinstance(r, dict))
    forksB = sum(r.get("forks_count", 0) for r in reposB if isinstance(r, dict))
    top_langB = langsB[0][0] if langsB else "N/A"
    active_hourB = sorted(hourB.items(), key=lambda x: x[1], reverse=True)[0][0] if hourB else "N/A"
    
    report = f"""# Laporan Perbandingan Developer GitPulse: @{userA} vs @{userB}
Dibuat secara otomatis pada {datetime.now().strftime('%d-%m-%Y %H:%M')}.

---

## Tabel Perbandingan Statistik

| Metrik Analisis | @{userA} | @{userB} |
| :--- | :---: | :---: |
| **Nama Lengkap** | {profileA.get("name") or "N/A"} | {profileB.get("name") or "N/A"} |
| **Repositori Publik** | {profileA.get("public_repos", 0)} | {profileB.get("public_repos", 0)} |
| **Pengikut (Followers)** | {profileA.get("followers", 0)} | {profileB.get("followers", 0)} |
| **Bahasa Utama** | {top_langA} | {top_langB} |
| **Jam Coding Aktif** | {active_hourA} | {active_hourB} |
| **Status Karakter** | {statusA} | {statusB} |
| **Total Bintang (Stars)** | {starsA} | {starsB} |
| **Total Fork** | {forksA} | {forksB} |

---

## Analisis Komparatif
- **@{userA}** tergolong sebagai **{statusA}** dengan total **{starsA}** bintang dan **{profileA.get("public_repos", 0)}** repositori publik.
- **@{userB}** tergolong sebagai **{statusB}** dengan total **{starsB}** bintang dan **{profileB.get("public_repos", 0)}** repositori publik.

*Laporan dihasilkan menggunakan GitPulse CLI Analyzer.*
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    console.print(f"[bold green]Laporan perbandingan sukses diekspor ke: [underline]{filename}[/underline][/bold green]\n")


def export_markdown_report(username, profile, sorted_langs, hour_percentages, sorted_repos, status, persona, events):
    filename = f"{username}_gitpulse_report.md"
    
    # Calculate values for copy-paste TUI badge card
    top_lang = sorted_langs[0][0] if sorted_langs else "N/A"
    top_lang_pct = sorted_langs[0][1] if sorted_langs else 0.0
    active_hour = "N/A"
    if hour_percentages:
        active_hour = sorted(hour_percentages.items(), key=lambda x: x[1], reverse=True)[0][0]

    # Generate flat clean contribution grid text for markdown
    month_row, grid_rows, summary_stats = generate_contribution_grid(events)
    clean_month_row = strip_rich_tags(month_row)
    clean_grid_rows = [strip_rich_tags(r) for r in grid_rows]
    
    grid_markdown_block = f"{clean_month_row}\n" + "\n".join(clean_grid_rows)

    # Style 1: Modern Single Line Box
    card_double = f"""┌─────────────────────────────────────────────────────────────┐
│                         GITPULSE                            │
│    Analitik Aktivitas & Karakter Developer GitHub           │
├─────────────────────────────────────────────────────────────┤
│  Username    : @{username:<43} │
│  Karakter    : {status:<43} │
│  Top Bahasa  : {top_lang:<27} ({top_lang_pct:0.1f}%) │
│  Waktu Aktif : {active_hour:<43} │
└─────────────────────────────────────────────────────────────┘"""

    # Style 2: Classic Minimalist Box
    card_minimal = f"""+-------------------------------------------------------------+
|                         GITPULSE                            |
|    Analitik Aktivitas & Karakter Developer GitHub           |
+-------------------------------------------------------------+
|  Username    : @{username:<43} |
|  Karakter    : {status:<43} |
|  Top Bahasa  : {top_lang:<27} ({top_lang_pct:0.1f}%) |
|  Waktu Aktif : {active_hour:<43} |
+-------------------------------------------------------------+"""

    # Style 3: Solid Block Badges
    card_badges = f"""===============================================================
  GITPULSE PROFILE CARD
===============================================================
  [Username]   @{username}
  [Karakter]   {status}
  [Top Bahasa] {top_lang} ({top_lang_pct:0.1f}%)
  [Waktu]      {active_hour}
==============================================================="""

    report_content = f"""# Laporan GitPulse - @{username}
Laporan Analitik Aktivitas GitHub Otomatis yang Dihasilkan pada {datetime.now().strftime('%d-%m-%Y %H:%M')}.

---

## Ringkasan Profil
- **Nama Lengkap:** {profile.get('name') or 'N/A'}
- **Lokasi:** {profile.get('location') or 'N/A'}
- **Bio:** {profile.get('bio') or 'Tidak ada bio.'}
- **Pengikut / Mengikuti:** {profile.get('followers')} / {profile.get('following')}
- **Repositori Publik:** {profile.get('public_repos')}

---

## Kalender Kontribusi (20 Minggu Terakhir)
```text
{grid_markdown_block}
```

### Ringkasan Aktivitas Kalender:
- **Total Kontribusi Terdeteksi:** {summary_stats['total']} kontribusi
- **Rata-rata Kontribusi Mingguan:** {summary_stats['rata_mingguan']:.1f}
- **Rata-rata Kontribusi Harian:** {summary_stats['rata_harian']:.2f}
- **Hari Teraktif:** {summary_stats['hari_teraktif']} ({summary_stats['hari_teraktif_count']} kontribusi)

---

## Repositori Terpopuler & Analisis Keaktifan
"""
    if sorted_repos:
        for idx, r in enumerate(sorted_repos, 1):
            lang_str = f" ({r.get('language')})" if r.get('language') else ""
            report_content += f"{idx}. **{r.get('name')}**{lang_str}  \n   [Stars: {r.get('stargazers_count', 0)} | Forks: {r.get('forks_count', 0)} | Status: {r['activity_status']}]\n"
    else:
        report_content += "Tidak ada repositori publik ditemukan.\n"

    report_content += f"""
---

## Bahasa Pemrograman Teratas
| Bahasa | Persentase Kontribusi |
| :--- | :---: |
"""
    for lang, pct in sorted_langs:
        report_content += f"| {lang} | {pct:.1f}% |\n"
        
    report_content += """
---

## Pola Waktu Kontribusi
| Kategori Waktu | Persentase Aktivitas |
| :--- | :---: |
"""
    for cat, pct in hour_percentages.items():
        report_content += f"| {cat} | {pct:.1f}% |\n"
        
    report_content += f"""
---

## Analisis Karakter Developer
- **Status Karakter:** **{status}**
- **Deskripsi Analisis:**  
  *"{persona}"*

---

## Kartu ASCII Profil (Salin ke Profile README Anda)
Pilih gaya kartu ASCII di bawah ini untuk mempercantik profil README GitHub Anda:

### Gaya 1: Box Border Modern
```text
{card_double}
```

### Gaya 2: Box Border Klasik Minimalis
```text
{card_minimal}
```

### Gaya 3: Solid Block Badges
```text
{card_badges}
```

---
*Dibuat menggunakan Alat CLI GitPulse*
"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    console.print(f"[bold green]Laporan sukses diekspor ke: [underline]{filename}[/underline][/bold green]\n")


def main():
    parser = argparse.ArgumentParser(description="GitPulse - GitHub Activity Visualizer & Persona Analyzer")
    parser.add_argument("-u", "--username", type=str, help="Username GitHub yang ingin dianalisis")
    parser.add_argument("-t", "--token", type=str, help="GitHub Personal Access Token (opsional)")
    parser.add_argument("-m", "--mock", action="store_true", help="Gunakan Demo Mock Data untuk uji coba instan")
    parser.add_argument("-c", "--compare", nargs=2, metavar=("USER1", "USER2"), help="Bandingkan dua username GitHub secara berdampingan")
    
    args = parser.parse_args()
    
    # Elegant interactive prompt menu if run without arguments
    if not args.username and not args.mock and not args.compare:
        console.print(Align.center(BANNER))
        console.print("[bold yellow]METODE EKSEKUSI GITPULSE[/bold yellow]")
        console.print("  [1] Analisis Akun Tunggal (Real-time API)")
        console.print("  [2] Bandingkan Dua Akun (Compare Mode)")
        console.print("  [3] Uji Coba Demo Instan (Mock Mode)")
        console.print("  [4] Keluar")
        choice = Prompt.ask("\nPilih opsi", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            username = Prompt.ask("\n[bold cyan]Masukkan Username GitHub[/bold cyan]")
            if not username.strip():
                console.print("[bold red]Error: Username tidak boleh kosong![/bold red]")
                sys.exit(1)
            args.username = username.strip()
        elif choice == "2":
            user1 = Prompt.ask("\n[bold cyan]Masukkan Username GitHub Pertama[/bold cyan]")
            user2 = Prompt.ask("[bold magenta]Masukkan Username GitHub Kedua[/bold magenta]")
            if not user1.strip() or not user2.strip():
                console.print("[bold red]Error: Username tidak boleh kosong![/bold red]")
                sys.exit(1)
            args.compare = [user1.strip(), user2.strip()]
        elif choice == "3":
            args.mock = True
        else:
            console.print("[bold white]Keluar dari GitPulse. Sampai jumpa![/bold white]")
            sys.exit(0)
            
    if args.compare:
        user1, user2 = args.compare
        if args.mock or (user1.lower() == "dev_pratama" and user2.lower() == "rivaldi01"):
            stats1 = {"profile": MOCK_PROFILE, "repos": MOCK_REPOS, "events": MOCK_EVENTS}
            stats2 = {"profile": MOCK_PROFILE_B, "repos": MOCK_REPOS_B, "events": MOCK_EVENTS_B}
            is_mock = True
        else:
            is_mock = False
            # Fetch with API
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                progress.add_task(description=f"Menghubungi API GitHub untuk @{user1}...", total=None)
                profile1, repos1, events1, mock_triggered1 = fetch_github_data(user1, args.token)
                
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                progress.add_task(description=f"Menghubungi API GitHub untuk @{user2}...", total=None)
                profile2, repos2, events2, mock_triggered2 = fetch_github_data(user2, args.token)
                
            stats1 = {"profile": profile1, "repos": repos1, "events": events1}
            stats2 = {"profile": profile2, "repos": repos2, "events": events2}
            is_mock = mock_triggered1 or mock_triggered2
            
        render_comparison_tui(user1, stats1, user2, stats2, is_mock)
        export_comparison_report(user1, stats1, user2, stats2)
        
    elif args.mock:
        profile, repos, events, is_mock = MOCK_PROFILE, MOCK_REPOS, MOCK_EVENTS, True
        sorted_langs, activity_counter, hour_percentages, weekday_percentages, sorted_repos = generate_statistics(repos, events)
        status, persona = get_developer_persona(activity_counter, hour_percentages)
        render_tui(profile, sorted_langs, activity_counter, hour_percentages, weekday_percentages, sorted_repos, status, persona, is_mock, events)
        export_markdown_report(profile["login"], profile, sorted_langs, hour_percentages, sorted_repos, status, persona, events)
        
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task(description=f"Menghubungi API GitHub untuk @{args.username}...", total=None)
            profile, repos, events, is_mock = fetch_github_data(args.username, args.token)
            
        sorted_langs, activity_counter, hour_percentages, weekday_percentages, sorted_repos = generate_statistics(repos, events)
        status, persona = get_developer_persona(activity_counter, hour_percentages)
        render_tui(profile, sorted_langs, activity_counter, hour_percentages, weekday_percentages, sorted_repos, status, persona, is_mock, events)
        export_markdown_report(profile["login"], profile, sorted_langs, hour_percentages, sorted_repos, status, persona, events)


if __name__ == "__main__":
    main()

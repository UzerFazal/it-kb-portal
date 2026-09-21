"""
Seed script: creates admin user, categories, and sample IT knowledge base articles.
Run: python scripts/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.models import User, Category, Article, Tag
from app.auth import hash_password

init_db()
db = SessionLocal()

# ── Users ─────────────────────────────────────────────
def get_or_create_user(username, email, password, role):
    u = db.query(User).filter(User.username == username).first()
    if not u:
        u = User(username=username, email=email, hashed_password=hash_password(password), role=role)
        db.add(u)
        db.flush()
    return u

admin = get_or_create_user("admin", "admin@company.local", "Admin123!", "admin")
user1 = get_or_create_user("jsmith", "jsmith@company.local", "User123!", "user")

# ── Categories ────────────────────────────────────────
cats_data = [
    ("Network & VPN", "network-vpn", "wifi", "Connectivity, VPN, Wi-Fi, remote access issues", 0,
     "Síť a VPN", "Připojení, VPN, Wi-Fi, problémy se vzdáleným přístupem"),
    ("Account & Access", "account-access", "lock", "Passwords, MFA, account lockouts, permissions", 1,
     "Účet a přístup", "Hesla, MFA, uzamčení účtu, oprávnění"),
    ("Email & Calendar", "email-calendar", "mail", "Outlook, Exchange, calendar sync, mail rules", 2,
     "E-mail a kalendář", "Outlook, Exchange, synchronizace kalendáře, pravidla pro poštu"),
    ("Printers & Peripherals", "printers-peripherals", "printer", "Printer setup, scanning, USB devices", 3,
     "Tiskárny a periferie", "Nastavení tiskárny, skenování, USB zařízení"),
    ("Hardware & Devices", "hardware-devices", "monitor", "Laptops, desktops, mobile phones, screens", 4,
     "Hardware a zařízení", "Notebooky, stolní počítače, mobilní telefony, obrazovky"),
    ("Software & Applications", "software-applications", "server", "Software installation, updates, licenses", 5,
     "Software a aplikace", "Instalace softwaru, aktualizace, licence"),
    ("Security", "security", "shield", "Antivirus, phishing, MFA, data protection", 6,
     "Zabezpečení", "Antivirus, phishing, MFA, ochrana dat"),
    ("Mobile & Remote Work", "mobile-remote", "smartphone", "Mobile devices, remote desktop, VDI", 7,
     "Mobilní a vzdálená práce", "Mobilní zařízení, vzdálená plocha, VDI"),
]
cats = {}
for name, slug, icon, desc, order, name_cs, desc_cs in cats_data:
    c = db.query(Category).filter(Category.slug == slug).first()
    if not c:
        c = Category(name=name, slug=slug, icon=icon, description=desc, order=order,
                      name_cs=name_cs, description_cs=desc_cs)
        db.add(c)
        db.flush()
    else:
        changed = False
        if not c.name_cs:
            c.name_cs = name_cs; changed = True
        if not c.description_cs:
            c.description_cs = desc_cs; changed = True
        if changed:
            db.add(c)
    cats[slug] = c

# ── Helper ────────────────────────────────────────────
def make_tag(name):
    from re import sub
    slug = sub(r'[^\w\s-]', '', name.lower())
    slug = sub(r'[\s_-]+', '-', slug).strip('-')
    t = db.query(Tag).filter(Tag.slug == slug).first()
    if not t:
        t = Tag(name=name, slug=slug)
        db.add(t)
        db.flush()
    return t

def add_article(title, slug, summary, content, cat_slug, tag_names,
                 title_cs=None, summary_cs=None, content_cs=None, published=True):
    existing = db.query(Article).filter(Article.slug == slug).first()
    if existing:
        # Backfill CS translations on an already-seeded article (safe re-run,
        # e.g. after a redeploy on a persisted DB).
        changed = False
        if title_cs and not existing.title_cs:
            existing.title_cs = title_cs; changed = True
        if summary_cs and not existing.summary_cs:
            existing.summary_cs = summary_cs; changed = True
        if content_cs and not existing.content_cs:
            existing.content_cs = content_cs; changed = True
        if changed:
            db.add(existing)
        return
    art = Article(
        title=title, slug=slug, summary=summary, content=content,
        title_cs=title_cs, summary_cs=summary_cs, content_cs=content_cs,
        category_id=cats[cat_slug].id, author_id=admin.id,
        is_published=published, views=0
    )
    for tn in tag_names:
        art.tags.append(make_tag(tn))
    db.add(art)

# ── Articles ──────────────────────────────────────────

add_article(
    title="VPN Connection Fails — Cannot Connect to Corporate Network",
    slug="vpn-connection-fails",
    summary="Step-by-step guide to troubleshoot and fix VPN connectivity issues on Windows and macOS.",
    cat_slug="network-vpn",
    tag_names=["vpn", "network", "remote access", "windows", "macos"],
    title_cs="Nefunguje VPN připojení — nelze se připojit k firemní síti",
    summary_cs="Podrobný návod krok za krokem pro odstranění problémů s VPN připojením na Windows a macOS.",
    content_cs="""<h2>Příznaky</h2>
<p>Zobrazí se chyba jako <code>Unable to connect</code>, <code>Authentication failed</code>, nebo se VPN klient při navazování spojení zasekne.</p>

<h2>Řešení krok za krokem</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Ověřte své internetové připojení</strong>
    <p>Otevřete prohlížeč a přejděte na libovolnou externí stránku (např. <code>google.com</code>). Pokud nemáte přístup k internetu, nejprve vyřešte problém s lokální sítí — VPN vyžaduje funkční internetové připojení.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Zkontrolujte přihlašovací údaje</strong>
    <p>Ujistěte se, že používáte své <strong>firemní uživatelské jméno</strong> (nikoli e-mailovou adresu) a aktuální heslo. Pokud jste heslo nedávno změnili, aktualizujte ho i ve VPN klientovi.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Restartujte VPN klienta</strong>
    <p>Úplně ukončete aplikaci VPN (zkontrolujte i ikonu v systémové liště). Počkejte 10 sekund, poté ji znovu otevřete a zkuste se připojit.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Vymažte DNS cache a resetujte síť</strong>
    <p>Na Windows otevřete příkazový řádek jako správce a spusťte:</p>
    <pre><code>ipconfig /flushdns
ipconfig /release
ipconfig /renew</code></pre>
    <p>Na macOS otevřete Terminál a spusťte:</p>
    <pre><code>sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder</code></pre>
  </div>
</div>

<div class="step-box">
  <div class="step-num">5</div>
  <div class="step-content">
    <strong>Přeinstalujte VPN klienta</strong>
    <p>Odinstalujte stávajícího VPN klienta přes Ovládací panely → Programy. Stáhněte nejnovější verzi z IT Self-Service portálu a znovu ji nainstalujte. Při vyzvání použijte své firemní přihlašovací údaje.</p>
  </div>
</div>

<h2>Stále to nefunguje?</h2>
<p>Pokud žádný z výše uvedených kroků problém nevyřeší, založte tiket na IT podporu a uveďte verzi VPN klienta a přesné znění chybové hlášky.</p>

<blockquote>Pokud pracujete z hotelu nebo veřejné Wi-Fi, některé sítě blokují VPN provoz na určitých portech. Zkuste přepnout mezi Wi-Fi a mobilním hotspotem.</blockquote>""",
    content="""<h2>Symptoms</h2>
<p>You receive an error such as <code>Unable to connect</code>, <code>Authentication failed</code>, or the VPN client freezes when trying to establish a connection.</p>

<h2>Step-by-Step Solution</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Verify your internet connection</strong>
    <p>Open a browser and navigate to any external website (e.g. <code>google.com</code>). If you have no internet access, troubleshoot your local network first — the VPN requires a working internet connection.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Check your credentials</strong>
    <p>Ensure you are using your <strong>corporate username</strong> (not your email address) and current password. If your password was recently changed, update it in the VPN client as well.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Restart the VPN client</strong>
    <p>Close the VPN application completely (check the system tray). Wait 10 seconds, then reopen and try connecting again.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Flush DNS and reset network</strong>
    <p>On Windows, open Command Prompt as Administrator and run:</p>
    <pre><code>ipconfig /flushdns
ipconfig /release
ipconfig /renew</code></pre>
    <p>On macOS, open Terminal and run:</p>
    <pre><code>sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder</code></pre>
  </div>
</div>

<div class="step-box">
  <div class="step-num">5</div>
  <div class="step-content">
    <strong>Reinstall the VPN client</strong>
    <p>Uninstall the existing VPN client via Control Panel → Programs. Download the latest version from the IT Self-Service Portal, then reinstall. Use your corporate credentials when prompted.</p>
  </div>
</div>

<h2>Still not working?</h2>
<p>If none of the above steps resolve the issue, submit a ticket to IT Support and include the VPN client version and the exact error message you see.</p>

<blockquote>If you are working from a hotel or public Wi-Fi, some networks block VPN traffic on certain ports. Try switching between Wi-Fi and a mobile hotspot.</blockquote>""",
)

add_article(
    title="How to Reset Your Corporate Password",
    slug="reset-corporate-password",
    summary="Instructions to self-service reset your password via the portal, or request an admin reset.",
    cat_slug="account-access",
    tag_names=["password", "account", "reset", "login"],
    title_cs="Jak obnovit firemní heslo",
    summary_cs="Postup pro svépomocné obnovení hesla přes portál, nebo jak požádat o obnovení heslo administrátorem.",
    content_cs="""<h2>Možnost A — Svépomocné obnovení hesla (SSPR)</h2>
<p>Pokud jste si dříve v systému zaregistrovali telefonní číslo nebo záložní e-mail, můžete si obnovit heslo bez kontaktování IT.</p>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Přejděte na portál pro obnovení hesla</strong>
    <p>Otevřete prohlížeč a přejděte na firemní stránku pro obnovení hesla: <code>https://password.company.local</code></p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Zadejte uživatelské jméno</strong>
    <p>Zadejte své firemní uživatelské jméno (část před <code>@</code> ve vaší e-mailové adrese) a klikněte na <strong>Next</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Ověřte svou identitu</strong>
    <p>Zvolte způsob ověření: SMS kód zaslaný na registrované mobilní číslo, nebo kód zaslaný na záložní e-mailovou adresu.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Nastavte nové heslo</strong>
    <p>Zadejte a potvrďte nové heslo. Musí splňovat požadavky bezpečnostní politiky:</p>
    <ul>
      <li>Minimálně 10 znaků</li>
      <li>Alespoň 1 velké písmeno, 1 malé písmeno, 1 číslice</li>
      <li>Nesmí se shodovat s posledními 5 hesly</li>
    </ul>
  </div>
</div>

<h2>Možnost B — Kontaktujte IT podporu</h2>
<p>Pokud SSPR není dostupné nebo se vám nedaří ověřit identitu, kontaktujte IT podporu přes portál Service Desk a požádejte o manuální obnovení hesla. Technik před zpracováním žádosti ověří vaši identitu.</p>

<blockquote>Po obnovení hesla nezapomeňte heslo aktualizovat všude, kde je uloženo: ve VPN klientovi, e-mailových aplikacích a na všech připojených mobilních zařízeních.</blockquote>""",
    content="""<h2>Option A — Self-Service Password Reset (SSPR)</h2>
<p>If you have previously registered your phone number or backup email in the system, you can reset your password without contacting IT.</p>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Go to the password reset portal</strong>
    <p>Open a browser and navigate to the corporate password reset page: <code>https://password.company.local</code></p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Enter your username</strong>
    <p>Type your corporate username (the part before the <code>@</code> in your email) and click <strong>Next</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Verify your identity</strong>
    <p>Choose a verification method: SMS code sent to your registered mobile number, or a code sent to your backup email address.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Set a new password</strong>
    <p>Enter and confirm your new password. It must meet the policy requirements:</p>
    <ul>
      <li>Minimum 10 characters</li>
      <li>At least 1 uppercase letter, 1 lowercase letter, 1 number</li>
      <li>Cannot match your last 5 passwords</li>
    </ul>
  </div>
</div>

<h2>Option B — Contact IT Support</h2>
<p>If SSPR is not available or you are unable to verify your identity, contact IT Support via the Service Desk portal and request a manual password reset. A technician will verify your identity before processing the request.</p>

<blockquote>After resetting your password, remember to update it in all places where it is saved: VPN client, mail applications, and any connected mobile devices.</blockquote>""",
)

add_article(
    title="Printer Not Found or Offline — Windows",
    slug="printer-offline-windows",
    summary="How to get a network printer back online and fix 'Printer offline' errors on Windows 10/11.",
    cat_slug="printers-peripherals",
    tag_names=["printer", "offline", "windows", "printing"],
    title_cs="Tiskárna nenalezena nebo offline — Windows",
    summary_cs="Jak dostat síťovou tiskárnu zpět online a opravit chybu 'Tiskárna offline' na Windows 10/11.",
    content_cs="""<h2>Příznaky</h2>
<p>Tiskárna se ve Windows zobrazuje jako <strong>Offline</strong>, tiskové úlohy jsou zaseknuté ve frontě, nebo se tiskárna v seznamu tiskáren vůbec neobjevuje.</p>

<h2>Rychlá řešení</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Zkontrolujte hardware tiskárny</strong>
    <p>Ujistěte se, že je tiskárna zapnutá, má vložený papír a na panelu neblikají žádné chybové kontrolky. Restartujte tiskárnu vypínačem.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Nastavte tiskárnu na "Use Printer Online"</strong>
    <p>Přejděte do <strong>Nastavení → Bluetooth a zařízení → Tiskárny a skenery</strong>. Klikněte na tiskárnu, poté na <strong>Otevřít tiskovou frontu</strong>. V nabídce klikněte na <strong>Tiskárna → Use Printer Online</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Vymažte tiskovou frontu</strong>
    <p>V okně tiskové fronty vyberte všechny úlohy (<code>Ctrl+A</code>) a stiskněte <code>Delete</code>. Pokud jsou úlohy zaseknuté, otevřete Služby (<code>Win+R</code> → <code>services.msc</code>), najděte <strong>Print Spooler</strong>, klikněte pravým tlačítkem a zvolte <strong>Restartovat</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Znovu přidejte síťovou tiskárnu</strong>
    <p>Pokud výše uvedené kroky nepomohou, odeberte tiskárnu z Windows a přidejte ji znovu. Přejděte do <strong>Nastavení → Tiskárny a skenery</strong>, klikněte na tiskárnu, poté <strong>Odebrat zařízení</strong>. Klikněte na <strong>Přidat tiskárnu nebo skener</strong> a postupujte podle průvodce pomocí IP adresy nebo hostname tiskárny.</p>
    <pre><code>IP tiskárny (příklad): 192.168.1.100
Nebo hostname: PRINTER-FLOOR2</code></pre>
  </div>
</div>

<h2>Stále to netiskne?</h2>
<p>Spusťte vestavěný nástroj pro řešení problémů s tiskárnou ve Windows: <strong>Nastavení → Systém → Poradce při potížích → Další nástroje pro řešení potíží → Tiskárna</strong>. Pokud problém přetrvává, založte tiket s uvedením modelu tiskárny a IP adresy.</p>""",
    content="""<h2>Symptoms</h2>
<p>The printer shows as <strong>Offline</strong> in Windows, print jobs are stuck in the queue, or the printer does not appear in the printer list at all.</p>

<h2>Quick Fixes</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Check the printer hardware</strong>
    <p>Make sure the printer is powered on, has paper loaded, and no error lights are flashing on its panel. Restart the printer using the power button.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Set the printer to "Use Printer Online"</strong>
    <p>Go to <strong>Settings → Bluetooth &amp; devices → Printers &amp; scanners</strong>. Click the printer, then click <strong>Open print queue</strong>. In the menu bar, click <strong>Printer → Use Printer Online</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Clear the print queue</strong>
    <p>In the print queue window, select all jobs (<code>Ctrl+A</code>) and press <code>Delete</code>. If jobs are stuck, open Services (<code>Win+R</code> → <code>services.msc</code>), find <strong>Print Spooler</strong>, right-click and select <strong>Restart</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Re-add the network printer</strong>
    <p>If the above steps do not help, remove the printer from Windows and add it again. Go to <strong>Settings → Printers &amp; scanners</strong>, click the printer, then <strong>Remove device</strong>. Click <strong>Add a printer or scanner</strong> and follow the wizard using the printer's IP address or hostname.</p>
    <pre><code>Printer IP (example): 192.168.1.100
Or hostname: PRINTER-FLOOR2</code></pre>
  </div>
</div>

<h2>Still not printing?</h2>
<p>Run the built-in Windows printer troubleshooter: <strong>Settings → System → Troubleshoot → Other troubleshooters → Printer</strong>. If the issue persists, raise a ticket including the printer model and IP address.</p>""",
)

add_article(
    title="Setting Up Corporate Email in Outlook (Desktop)",
    slug="email-setup-outlook-desktop",
    summary="How to configure your corporate Exchange/Microsoft 365 mailbox in Outlook 2019/2021/365.",
    cat_slug="email-calendar",
    tag_names=["email", "outlook", "exchange", "microsoft 365", "setup"],
    title_cs="Nastavení firemního e-mailu v Outlooku (desktop)",
    summary_cs="Jak nastavit firemní Exchange/Microsoft 365 schránku v Outlooku 2019/2021/365.",
    content_cs="""<h2>Požadavky</h2>
<ul>
  <li>Nainstalovaný Microsoft Outlook 2019, 2021 nebo Microsoft 365</li>
  <li>Firemní e-mailová adresa a heslo</li>
  <li>Aktivní síťové připojení (v kanceláři nebo přes VPN)</li>
</ul>

<h2>Kroky nastavení</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Otevřete Outlook poprvé</strong>
    <p>Spusťte Outlook. Pokud jde o novou instalaci, průvodce nastavením se spustí automaticky. Pokud je Outlook již nastaven s jiným účtem, přejděte na <strong>Soubor → Přidat účet</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Zadejte svou e-mailovou adresu</strong>
    <p>Zadejte celou firemní e-mailovou adresu (např. <code>jmeno.prijmeni@company.com</code>) a klikněte na <strong>Connect</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Přihlaste se firemními údaji</strong>
    <p>Outlook vás přesměruje na firemní přihlašovací stránku. Zadejte heslo a dokončete MFA (pokud je vyžadováno). Na sdílených počítačích <strong>nezaškrtávejte</strong> "Zůstat přihlášen".</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Počkejte na synchronizaci schránky</strong>
    <p>Outlook začne synchronizovat vaši schránku. U velkých schránek (10+ GB) může první synchronizace trvat 15–30 minut. E-mail můžete začít používat okamžitě, synchronizace probíhá na pozadí.</p>
  </div>
</div>

<h2>Řešení problémů</h2>
<p>Pokud Outlook ve stavovém řádku zobrazuje <strong>"Disconnected"</strong> nebo <strong>"Trying to connect"</strong>:</p>
<ol>
  <li>Ověřte, že jste připojeni k firemní síti nebo VPN.</li>
  <li>Zkontrolujte, zda heslo nevypršelo (zkuste se přihlásit přes webmail na <code>mail.company.com</code>).</li>
  <li>Restartujte Outlook.</li>
</ol>""",
    content="""<h2>Prerequisites</h2>
<ul>
  <li>Microsoft Outlook 2019, 2021, or Microsoft 365 installed</li>
  <li>Your corporate email address and password</li>
  <li>Active network connection (on-site or via VPN)</li>
</ul>

<h2>Setup Steps</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Open Outlook for the first time</strong>
    <p>Launch Outlook. If this is a fresh install, the setup wizard starts automatically. If Outlook is already configured with a different account, go to <strong>File → Add Account</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Enter your email address</strong>
    <p>Type your full corporate email address (e.g. <code>firstname.lastname@company.com</code>) and click <strong>Connect</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Sign in with corporate credentials</strong>
    <p>Outlook will redirect you to the corporate sign-in page. Enter your password and complete MFA (if prompted). Do <strong>not</strong> check "Stay signed in" on shared computers.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Wait for mailbox synchronization</strong>
    <p>Outlook will begin syncing your mailbox. For large mailboxes (10+ GB) this may take 15–30 minutes on first setup. You can start using email immediately while it syncs in the background.</p>
  </div>
</div>

<h2>Troubleshooting</h2>
<p>If Outlook shows <strong>"Disconnected"</strong> or <strong>"Trying to connect"</strong> in the status bar:</p>
<ol>
  <li>Verify you are connected to the corporate network or VPN.</li>
  <li>Check that your password has not expired (try logging in via webmail at <code>mail.company.com</code>).</li>
  <li>Restart Outlook.</li>
</ol>""",
)

add_article(
    title="Account Locked — How to Unlock Your Domain Account",
    slug="account-locked-unlock",
    summary="What to do when your Windows or domain account is locked and you cannot log in.",
    cat_slug="account-access",
    tag_names=["account", "locked", "login", "active directory"],
    title_cs="Uzamčený účet — jak odemknout doménový účet",
    summary_cs="Co dělat, když je váš Windows nebo doménový účet uzamčen a nemůžete se přihlásit.",
    content_cs="""<h2>Proč se můj účet uzamyká?</h2>
<p>Firemní bezpečnostní politika uzamyká účty po <strong>5 po sobě jdoucích neúspěšných pokusech o přihlášení</strong>. Časté příčiny:</p>
<ul>
  <li>Zadání špatného hesla (např. zapnutý CapsLock)</li>
  <li>Zastaralé uložené přihlašovací údaje ve Správci přihlašovacích údajů Windows</li>
  <li>Mobilní zařízení se pokouší synchronizovat se starým heslem</li>
  <li>Více vzdálených relací se pokouší o autentizaci současně</li>
</ul>

<h2>Jak účet odemknout</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Počkejte 15 minut</strong>
    <p>Účty se automaticky odemykají po 15 minutách uzamčení. Pokud nepotřebujete okamžitý přístup, jednoduše počkejte a zkuste to znovu.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Použijte SSPR (svépomocné odemčení)</strong>
    <p>Přejděte na <code>https://password.company.local</code>, zadejte uživatelské jméno a zvolte <strong>Unlock my account</strong> (místo obnovení hesla). Ověřte identitu přes SMS nebo záložní e-mail.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Kontaktujte IT podporu</strong>
    <p>Pokud SSPR není dostupné, kontaktujte Service Desk. Technik ověří vaši identitu a účet ručně odemkne. Obvykle to trvá méně než 5 minut.</p>
  </div>
</div>

<h2>Jak předejít dalšímu uzamčení</h2>
<ul>
  <li>Po změně hesla ho aktualizujte na <strong>všech zařízeních</strong>: notebook, telefon, tablet.</li>
  <li>Vymažte uložené přihlašovací údaje ve <strong>Správci přihlašovacích údajů Windows</strong> (Ovládací panely → Správce přihlašovacích údajů → Windows Credentials).</li>
  <li>Pokud používáte Outlook na mobilu, přejděte do nastavení pošty a zadejte nové heslo znovu.</li>
</ul>""",
    content="""<h2>Why Does My Account Get Locked?</h2>
<p>The corporate security policy locks accounts after <strong>5 consecutive failed login attempts</strong>. Common causes:</p>
<ul>
  <li>Typing the wrong password (e.g. CapsLock on)</li>
  <li>Outdated saved credentials in Windows Credential Manager</li>
  <li>A mobile device trying to sync with an old password</li>
  <li>Multiple remote sessions attempting to authenticate simultaneously</li>
</ul>

<h2>How to Unlock</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Wait 15 minutes</strong>
    <p>Accounts unlock automatically after a 15-minute lockout period. If you do not need immediate access, simply wait and try again.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Use SSPR (self-service unlock)</strong>
    <p>Go to <code>https://password.company.local</code>, enter your username, and choose <strong>Unlock my account</strong> (instead of reset password). Verify your identity via SMS or backup email.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Contact IT Support</strong>
    <p>If SSPR is unavailable, contact the Service Desk. The technician will verify your identity and manually unlock the account. This usually takes under 5 minutes.</p>
  </div>
</div>

<h2>Preventing Future Lockouts</h2>
<ul>
  <li>After changing your password, update it on <strong>all devices</strong>: laptop, phone, tablet.</li>
  <li>Clear saved credentials in <strong>Windows Credential Manager</strong> (Control Panel → Credential Manager → Windows Credentials).</li>
  <li>If using Outlook on mobile, go to mail settings and re-enter the new password.</li>
</ul>""",
)

add_article(
    title="Cannot Access Shared Folder — Access Denied or Not Found",
    slug="shared-folder-access-denied",
    summary="Troubleshooting steps for 'Access Denied' or missing shared network drives.",
    cat_slug="account-access",
    tag_names=["shared drive", "network folder", "access denied", "permissions"],
    title_cs="Nelze přistoupit ke sdílené složce — Přístup odepřen nebo nenalezeno",
    summary_cs="Postup řešení chyby 'Přístup odepřen' nebo chybějících sdílených síťových disků.",
    content_cs="""<h2>Příznaky</h2>
<p>Při pokusu o otevření sdílené síťové složky (např. <code>\\\\server\\department</code>) se zobrazí <em>"Access is denied"</em>, <em>"The network path was not found"</em>, nebo písmeno disku v Průzkumníku souborů chybí.</p>

<h2>Postup řešení</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Zkontrolujte síťové připojení a VPN</strong>
    <p>Sdílené disky jsou dostupné pouze ve firemní síti nebo přes VPN. Pokud pracujete vzdáleně, ujistěte se, že je VPN připojena.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Znovu namapujte síťový disk</strong>
    <p>Otevřete Průzkumníka souborů, klikněte pravým tlačítkem na <strong>Tento počítač</strong>, zvolte <strong>Připojit síťovou jednotku</strong>. Zadejte UNC cestu (např. <code>\\\\fileserver01\\shared</code>) a zaškrtněte <strong>Znovu připojit při přihlášení</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Ověřte svá oprávnění</strong>
    <p>Pokud se ke složce dostanete, ale vidíte <em>"Access Denied"</em>, možná nemáte oprávnění. Ověřte u svého manažera, zda byste měli mít přístup, poté založte tiket na Service Desk s žádostí o přístup. Oprávnění spravuje IT administrátor vašeho oddělení.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Restartujte službu Workstation</strong>
    <p>Otevřete PowerShell jako správce a spusťte:</p>
    <pre><code>Restart-Service LanmanWorkstation -Force</code></pre>
    <p>Poté zkuste přístup ke sdílené složce znovu.</p>
  </div>
</div>

<blockquote>Pokud byly disky namapovány přes přihlašovací skript zásad skupiny (Group Policy), odhlaste se a znovu přihlaste, aby se mapovací skript znovu spustil.</blockquote>""",
    content="""<h2>Symptoms</h2>
<p>When you try to open a shared network folder (e.g. <code>\\\\server\\department</code>), you see <em>"Access is denied"</em>, <em>"The network path was not found"</em>, or the drive letter is missing from File Explorer.</p>

<h2>Troubleshooting Steps</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Check your network connection and VPN</strong>
    <p>Shared drives are only accessible on the corporate network or via VPN. Ensure VPN is connected if you are working remotely.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Re-map the network drive</strong>
    <p>Open File Explorer, right-click <strong>This PC</strong>, select <strong>Map network drive</strong>. Enter the UNC path (e.g. <code>\\\\fileserver01\\shared</code>) and check <strong>Reconnect at sign-in</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Verify your permissions</strong>
    <p>If you can reach the folder but see <em>"Access Denied"</em>, you may not have permission. Check with your manager whether you should have access, then raise a Service Desk ticket to request access. Permissions are managed by your department's IT admin.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Restart the Workstation service</strong>
    <p>Open PowerShell as Administrator and run:</p>
    <pre><code>Restart-Service LanmanWorkstation -Force</code></pre>
    <p>Then try accessing the share again.</p>
  </div>
</div>

<blockquote>If drives were mapped via a Group Policy login script, sign out and sign back in to re-run the mapping script.</blockquote>""",
)

add_article(
    title="Laptop Running Slow — Performance Troubleshooting",
    slug="laptop-running-slow",
    summary="Common reasons why a corporate laptop becomes slow and how to improve performance.",
    cat_slug="hardware-devices",
    tag_names=["laptop", "performance", "slow", "windows"],
    title_cs="Notebook je pomalý — řešení výkonu",
    summary_cs="Časté příčiny zpomalení firemního notebooku a jak zlepšit výkon.",
    content_cs="""<h2>Časté příčiny</h2>
<ul>
  <li>Příliš mnoho programů na pozadí při spuštění</li>
  <li>Málo místa na disku (méně než 10 % volného místa)</li>
  <li>Antivirus provádí kontrolu na pozadí</li>
  <li>Probíhá Windows Update nebo nasazení softwaru</li>
  <li>Nedostatečná RAM pro aktuální zátěž</li>
</ul>

<h2>Rychlá řešení</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Restartujte počítač</strong>
    <p>Obyčejný restart uvolní paměť a aplikuje čekající aktualizace. Nestačí uzamknout obrazovku nebo uspat — proveďte plný restart přes <strong>Start → Napájení → Restartovat</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Zkontrolujte volné místo na disku</strong>
    <p>Otevřete Průzkumníka souborů, klikněte pravým tlačítkem na disk <strong>C:</strong>, zvolte <strong>Vlastnosti</strong>. Pokud je volné místo pod 10 GB, vyprázdněte Koš a spusťte Čištění disku (<code>cleanmgr</code>). Přesuňte velké soubory na síťové úložiště nebo do OneDrive.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Zakažte zbytečné programy při spuštění</strong>
    <p>Stiskněte <code>Ctrl+Shift+Esc</code> pro otevření Správce úloh. Přejděte na kartu <strong>Po spuštění</strong>. Klikněte pravým tlačítkem na programy s <em>vysokým</em> dopadem, které při startu nepotřebujete, a zvolte <strong>Zakázat</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Zkontrolujte vysoké vytížení CPU/RAM</strong>
    <p>Ve Správci úloh klikněte na kartu <strong>Procesy</strong> a seřaďte podle CPU nebo paměti. Identifikujte procesy spotřebovávající nadměrné množství zdrojů. Pokud neznámý proces spotřebovává hodně CPU, nahlaste to IT — může jít o zaseklou aktualizaci nebo kontrolu malwaru.</p>
  </div>
</div>

<h2>Pokud problém přetrvává</h2>
<p>Založte tiket na kontrolu hardwaru se sériovým číslem notebooku (najdete na štítku na spodní straně nebo v <strong>Nastavení → Systém → O systému</strong>). IT může doporučit upgrade RAM nebo přeinstalaci systému.</p>""",
    content="""<h2>Common Causes</h2>
<ul>
  <li>Too many startup programs</li>
  <li>Low disk space (less than 10% free)</li>
  <li>Antivirus scanning running in the background</li>
  <li>Windows Update or software deployment in progress</li>
  <li>RAM insufficient for current workload</li>
</ul>

<h2>Quick Fixes</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Restart the computer</strong>
    <p>A simple restart clears memory leaks and applies pending updates. Do not just lock or sleep — perform a full restart via <strong>Start → Power → Restart</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Check disk space</strong>
    <p>Open File Explorer, right-click the <strong>C:</strong> drive, select <strong>Properties</strong>. If free space is under 10 GB, clear the Recycle Bin and run Disk Cleanup (<code>cleanmgr</code>). Move large files to the network share or OneDrive.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Disable unnecessary startup programs</strong>
    <p>Press <code>Ctrl+Shift+Esc</code> to open Task Manager. Go to the <strong>Startup</strong> tab. Right-click programs with <em>High</em> impact that you do not need at startup and select <strong>Disable</strong>.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Check for high CPU/RAM usage</strong>
    <p>In Task Manager, click the <strong>Processes</strong> tab and sort by CPU or Memory. Identify processes consuming excessive resources. If a process you don't recognize is using a lot of CPU, report it to IT — it may be a runaway update or malware scan.</p>
  </div>
</div>

<h2>If the Issue Persists</h2>
<p>Submit a hardware review ticket with the laptop's serial number (found on the sticker underneath or in <strong>Settings → System → About</strong>). IT may recommend a RAM upgrade or OS reinstall.</p>""",
)

add_article(
    title="Phishing Email — What to Do If You Received a Suspicious Email",
    slug="phishing-email-guide",
    summary="How to identify phishing emails and the correct steps to report them to IT Security.",
    cat_slug="security",
    tag_names=["phishing", "security", "email", "malware"],
    title_cs="Phishingový e-mail — co dělat, když dostanete podezřelý e-mail",
    summary_cs="Jak rozpoznat phishingové e-maily a správný postup jejich nahlášení IT bezpečnosti.",
    content_cs="""<h2>Jak rozpoznat phishingový e-mail</h2>
<p>Phishingové e-maily mají obvykle jeden nebo více z těchto znaků:</p>
<ul>
  <li>Naléhavý tón: <em>"Váš účet bude do 24 hodin uzavřen"</em></li>
  <li>Podezřelá adresa odesílatele (např. <code>support@company-helpdesk.xyz</code>)</li>
  <li>Odkazy, které po najetí myší neodpovídají firemní doméně</li>
  <li>Neočekávané přílohy (zejména <code>.zip</code>, <code>.exe</code> nebo soubory Office)</li>
  <li>Obecné oslovení (<em>"Dear User"</em> místo vašeho jména)</li>
  <li>Žádosti o hesla, údaje platební karty nebo osobní údaje</li>
</ul>

<h2>Co dělat — krok za krokem</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>NEKLIKEJTE na žádné odkazy ani neotvírejte přílohy</strong>
    <p>I pouhý náhled některých příloh může spustit škodlivý kód. Nepřeposílejte e-mail kolegům.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Nahlaste e-mail tlačítkem Report Phishing</strong>
    <p>V Outlooku vyberte podezřelý e-mail a klikněte na tlačítko <strong>Report Phishing</strong> na pásu karet (karta Domů → sekce Report). E-mail se tím odešle bezpečnostnímu týmu k analýze.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>Pokud jste klikli na odkaz nebo otevřeli přílohu</strong>
    <p>Okamžitě se odpojte od sítě (odpojte LAN kabel nebo vypněte Wi-Fi) a zavolejte na linku IT bezpečnosti. Počítač nevypínejte — IT může potřebovat vyšetřit, co se stalo.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Okamžitě si změňte heslo (pokud jste zadali přihlašovací údaje)</strong>
    <p>Pokud jste na podezřelé stránce zadali uživatelské jméno/heslo, ihned přejděte na SSPR portál a heslo změňte. Informujte IT bezpečnost, aby mohla zkontrolovat neoprávněný přístup.</p>
  </div>
</div>

<blockquote>Pamatujte: IT si <strong>nikdy</strong> nebude vyžadovat vaše heslo přes e-mail nebo telefon. Pokud vás o heslo požádá někdo, kdo tvrdí, že je z IT, odmítněte a nahlaste to.</blockquote>""",
    content="""<h2>How to Identify a Phishing Email</h2>
<p>Phishing emails typically have one or more of these characteristics:</p>
<ul>
  <li>Urgent language: <em>"Your account will be closed in 24 hours"</em></li>
  <li>Suspicious sender address (e.g. <code>support@company-helpdesk.xyz</code>)</li>
  <li>Links that do not match the company domain when you hover over them</li>
  <li>Attachments you did not expect (especially <code>.zip</code>, <code>.exe</code>, or Office files)</li>
  <li>Generic greetings (<em>"Dear User"</em> instead of your name)</li>
  <li>Requests for passwords, credit card details, or personal data</li>
</ul>

<h2>What to Do — Step by Step</h2>

<div class="step-box">
  <div class="step-num">1</div>
  <div class="step-content">
    <strong>Do NOT click any links or open attachments</strong>
    <p>Even previewing certain attachments can execute malicious code. Do not forward the email to colleagues.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">2</div>
  <div class="step-content">
    <strong>Report the email using the Report Phishing button</strong>
    <p>In Outlook, select the suspicious email and click the <strong>Report Phishing</strong> button in the ribbon (Home tab → Report section). This sends the email to the Security team for analysis.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">3</div>
  <div class="step-content">
    <strong>If you clicked a link or opened an attachment</strong>
    <p>Immediately disconnect from the network (unplug the LAN cable or disable Wi-Fi) and call IT Security at the emergency line. Do not shut down the computer — IT may need to investigate what happened.</p>
  </div>
</div>

<div class="step-box">
  <div class="step-num">4</div>
  <div class="step-content">
    <strong>Change your password immediately (if you entered credentials)</strong>
    <p>If you submitted your username/password on a suspicious page, go to the SSPR portal immediately and change your password. Notify IT Security so they can check for unauthorized access.</p>
  </div>
</div>

<blockquote>Remember: IT will <strong>never</strong> ask for your password via email or phone. If someone claiming to be from IT asks for your password, refuse and report the incident.</blockquote>""",
)

db.commit()
db.close()
print("✓ Database seeded successfully.")
print("  Admin login: admin / Admin123!")
print("  User login:  jsmith / User123!")

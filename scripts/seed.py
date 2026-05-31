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
    ("Network & VPN", "network-vpn", "wifi", "Connectivity, VPN, Wi-Fi, remote access issues", 0),
    ("Account & Access", "account-access", "lock", "Passwords, MFA, account lockouts, permissions", 1),
    ("Email & Calendar", "email-calendar", "mail", "Outlook, Exchange, calendar sync, mail rules", 2),
    ("Printers & Peripherals", "printers-peripherals", "printer", "Printer setup, scanning, USB devices", 3),
    ("Hardware & Devices", "hardware-devices", "monitor", "Laptops, desktops, mobile phones, screens", 4),
    ("Software & Applications", "software-applications", "server", "Software installation, updates, licenses", 5),
    ("Security", "security", "shield", "Antivirus, phishing, MFA, data protection", 6),
    ("Mobile & Remote Work", "mobile-remote", "smartphone", "Mobile devices, remote desktop, VDI", 7),
]
cats = {}
for name, slug, icon, desc, order in cats_data:
    c = db.query(Category).filter(Category.slug == slug).first()
    if not c:
        c = Category(name=name, slug=slug, icon=icon, description=desc, order=order)
        db.add(c)
        db.flush()
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

def add_article(title, slug, summary, content, cat_slug, tag_names, published=True):
    if db.query(Article).filter(Article.slug == slug).first():
        return
    art = Article(
        title=title, slug=slug, summary=summary, content=content,
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

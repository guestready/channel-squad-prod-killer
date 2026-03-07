"""Seed the database with test data. Only runs if the DB is empty."""
from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session

from . import models


_USERS = [
    {"name": "Alice Chen", "team": "Platform", "nickname": "The Destroyer"},
    {"name": "Bob Martinez", "team": "Backend", "nickname": None},
    {"name": "Charlie Kim", "team": "Frontend", "nickname": "CSS Whisperer"},
    {"name": "Diana Patel", "team": "Platform", "nickname": "kubectl Queen"},
    {"name": "Evan Torres", "team": "Backend", "nickname": "The One-Liner"},
    {"name": "Fiona Reyes", "team": "Frontend", "nickname": None},
    {"name": "George Nakamura", "team": "Backend", "nickname": "Null Pointer"},
    {"name": "Hannah Osei", "team": "Platform", "nickname": None},
    {"name": "Ivan Petrov", "team": "Frontend", "nickname": "The Refresher"},
    {"name": "Julia Santos", "team": "Backend", "nickname": "Ship It"},
]

_INCIDENT_TEMPLATES = [
    {
        "title": "Dropped the production database",
        "description": "Ran a migration script against prod instead of staging. The script had a DROP TABLE in it. It worked as intended.",
        "discovered_by": "Monitoring alert: 0 rows returned from every query",
        "resolved_by": "Restored from last night's backup. Lost 6 hours of data. Nobody was happy.",
        "helpers": "Bob Martinez, the DBA who was supposed to be on vacation",
        "links": "https://example.com/postmortem-001",
    },
    {
        "title": "Deployed to production on a Friday at 4:55 PM",
        "description": "It was 'just a config change'. The config change disabled authentication on the payment API.",
        "discovered_by": "A user emailed support saying they could see other people's orders",
        "resolved_by": "Emergency rollback. The engineer's weekend was not as planned.",
        "helpers": "Diana Patel, who was already in the parking lot",
        "links": "",
    },
    {
        "title": "CSS change took down checkout",
        "description": "Updated the button styles. The z-index change caused the checkout button to be hidden behind an invisible div on mobile. Revenue stopped.",
        "discovered_by": "Sales team noticed the revenue dashboard flatline mid-afternoon",
        "resolved_by": "Reverted the CSS. Added z-index to the list of things that require a second pair of eyes.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Kubernetes pod memory limit set to 1MB",
        "description": "Typo in the Helm values file. The pod kept OOMKilling every 3 seconds for 45 minutes before anyone noticed the alerts.",
        "discovered_by": "PagerDuty. Everyone's phones went off simultaneously in the all-hands meeting.",
        "resolved_by": "Fixed the YAML. Redeployed. Added a validator to catch this in CI.",
        "helpers": "Evan Torres",
        "links": "https://example.com/incident-k8s-oom",
    },
    {
        "title": "Infinite loop in background job ate $4,000 of AWS credits",
        "description": "A while True loop with no sleep and no break condition. It ran for 11 hours overnight querying the external API in a tight loop.",
        "discovered_by": "AWS billing alert at 3 AM",
        "resolved_by": "Killed the process. Called AWS support. Cried a little.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "git push --force to main",
        "description": "Thought it was a feature branch. It was not. Two weeks of commits from 6 engineers were gone for 8 minutes.",
        "discovered_by": "Slack message: 'why is my branch ahead of main by 847 commits'",
        "resolved_by": "git reflog to the rescue. Everything recovered. Trust not recovered.",
        "helpers": "Alice Chen (very reluctantly)",
        "links": "",
    },
    {
        "title": "Sent test email to entire customer list",
        "description": "Was testing the newsletter template. The environment variable SEND_REAL_EMAILS was set to true in .env. 47,000 customers received an email that said 'TEST EMAIL PLEASE IGNORE xoxo'.",
        "discovered_by": "The reply-all responses started immediately",
        "resolved_by": "Sent an apology email. Open rate was 89%. Highest engagement ever.",
        "helpers": "Marketing team (eventually forgave)",
        "links": "",
    },
    {
        "title": "Deleted the wrong S3 bucket",
        "description": "The bucket names were very similar. One was 'prod-assets', the other was 'prod-assets-backup'. Deleted the backup. Then deleted prod-assets by mistake while panicking.",
        "discovered_by": "The website stopped loading images",
        "resolved_by": "S3 versioning was enabled on one of the buckets. Some assets recovered. Some were gone forever.",
        "helpers": "Bob Martinez, Diana Patel",
        "links": "https://example.com/s3-incident",
    },
    {
        "title": "API rate limit set to 1 request per hour",
        "description": "Meant to type 1000. Typed 1. The config was deployed at midnight and nobody noticed until business hours when every API client started failing.",
        "discovered_by": "Support ticket flood starting at 9:02 AM",
        "resolved_by": "Config update and redeploy. Root cause: no unit tests for config validation.",
        "helpers": "Fiona Reyes",
        "links": "",
    },
    {
        "title": "Cron job scheduled for every minute instead of every month",
        "description": "* * * * * vs 0 0 1 * *. One character difference. The job sent a 'Monthly Summary Report' email every minute to every manager in the company.",
        "discovered_by": "CTO replied to the 47th email asking what was happening",
        "resolved_by": "Killed the cron job. Sent one more email to apologize. Added cron syntax linting to CI.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Hardcoded production credentials in public GitHub repo",
        "description": "Was working fast. Pushed API keys to a public repo. The keys were rotated by the automated secret scanner 4 minutes later but someone had already cloned the repo.",
        "discovered_by": "GitHub secret scanning alert",
        "resolved_by": "Rotated all credentials. Audited access logs. Nothing exploited (probably).",
        "helpers": "Security team",
        "links": "",
    },
    {
        "title": "TLS certificate expired on the homepage",
        "description": "The auto-renewal script had been silently failing for 30 days. Nobody noticed because the monitoring alert email was going to a distribution list that nobody checked.",
        "discovered_by": "A user tweeted a screenshot of the 'Your connection is not private' warning",
        "resolved_by": "Manually renewed the certificate. Fixed the renewal script. Subscribed a real human to the alert list.",
        "helpers": "Charlie Kim, Evan Torres",
        "links": "",
    },
    {
        "title": "Accidentally set everyone's account balance to 0",
        "description": "Data migration script had a bug where it set the default value instead of preserving the existing one. Ran in production because staging 'passed'.",
        "discovered_by": "User support tickets. Many. All urgent.",
        "resolved_by": "Restored from backup taken 2 hours before the migration. 2 hours of transactions manually re-applied.",
        "helpers": "Alice Chen, Bob Martinez, Diana Patel",
        "links": "https://example.com/migration-disaster",
    },
    {
        "title": "Enabled debug mode in production",
        "description": "DEBUG=True in the production Django settings. Full stack traces with local variables were being shown to users on any error page. For 3 days.",
        "discovered_by": "A user sent a screenshot of an error page showing database passwords",
        "resolved_by": "Set DEBUG=False. Redeployed. Rotated every secret that appeared in any stack trace.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Broke search for everyone named O'Brien",
        "description": "SQL query was built with string concatenation. Any search with an apostrophe caused a syntax error. The bug was reported 14 months ago. PR to fix it was still open.",
        "discovered_by": "Customer complaint. The customer's name was O'Brien.",
        "resolved_by": "Merged the 14-month-old PR. Closed 23 duplicate bug reports.",
        "helpers": "Fiona Reyes",
        "links": "",
    },
    {
        "title": "Misconfigured nginx sent all traffic to localhost:3000",
        "description": "Copy-pasted an nginx config from a blog post without reading it. The upstream was set to localhost. Worked fine on the server that had a dev process running.",
        "discovered_by": "Uptime monitor. All health checks failed within 2 minutes of deploy.",
        "resolved_by": "Reverted nginx config. Wrote an actual test for the config before deploying.",
        "helpers": "Hannah Osei",
        "links": "",
    },
    {
        "title": "Ran TRUNCATE on the users table instead of the sessions table",
        "description": "Both queries were open in different tabs. Executed the wrong one. 230,000 users had to re-register.",
        "discovered_by": "Login stopped working for everyone instantly",
        "resolved_by": "Restored from the 15-minute automated snapshot. Lost 15 minutes of signups.",
        "helpers": "Alice Chen, Ivan Petrov",
        "links": "",
    },
    {
        "title": "Feature flag defaulted to ON in production",
        "description": "New checkout redesign was meant to be dark-launched to 0% of users. The flag logic was inverted. 100% of users got the half-finished redesign for 4 hours.",
        "discovered_by": "Conversion rate dropped 60% immediately",
        "resolved_by": "Flipped the flag. Added a test that verifies flag defaults before deploy.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Deployed with wrong environment variables",
        "description": "The CI pipeline was pointing to a .env.staging file that had been deleted. Fell back to defaults. The default database URL pointed to prod from a different region.",
        "discovered_by": "Duplicate write errors started appearing in logs",
        "resolved_by": "Corrected the env config. Added validation that required vars are explicitly set.",
        "helpers": "George Nakamura",
        "links": "",
    },
    {
        "title": "Redis cache key collision wiped personalized data for all users",
        "description": "Added a new cache key with the same prefix as user session keys. A cache flush cleared all active sessions at 2 PM on a Tuesday.",
        "discovered_by": "Everyone was suddenly logged out at the same time",
        "resolved_by": "Namespaced all cache keys. 50,000 users had to log back in.",
        "helpers": "Julia Santos",
        "links": "",
    },
    {
        "title": "Accidentally whitelisted 0.0.0.0/0 in the security group",
        "description": "Was trying to debug a connectivity issue. Temporarily opened all inbound traffic. Forgot to revert. The security team found it during a routine audit 11 days later.",
        "discovered_by": "Security audit",
        "resolved_by": "Reverted the rule. Conducted a full access log review. Nothing breached (as far as we know).",
        "helpers": "Security team",
        "links": "",
    },
    {
        "title": "Merge conflict resolution deleted the input sanitization",
        "description": "During a complex merge, the section that stripped HTML from user inputs was removed. User-submitted HTML started rendering in the app for 6 hours.",
        "discovered_by": "A user submitted <marquee>hello</marquee> in a comment and it rendered",
        "resolved_by": "Hotfix deployed. Sanitized all affected content in the database.",
        "helpers": "Charlie Kim, Fiona Reyes",
        "links": "",
    },
    {
        "title": "Timezone bug made all appointments show up a day early",
        "description": "Switched from UTC to local time in the display layer without adjusting the storage layer. Every scheduled appointment appeared 5 hours early for users in EST.",
        "discovered_by": "Customer support was overwhelmed with 'my appointment disappeared' tickets",
        "resolved_by": "Reverted the timezone change. Properly handled TZ conversion end-to-end.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Logging every request body to CloudWatch",
        "description": "Added verbose logging for debugging. Forgot to remove it. Every POST body including passwords and credit card numbers was being logged in plaintext for 9 days.",
        "discovered_by": "Security engineer noticed unusually large CloudWatch bills",
        "resolved_by": "Removed the logging. Purged the log streams. Notified legal.",
        "helpers": "Hannah Osei, security team",
        "links": "",
    },
    {
        "title": "Schema migration broke the ORM model",
        "description": "Renamed a column in the database but forgot to update the SQLAlchemy model. The app deployed fine. Queries started failing at runtime.",
        "discovered_by": "Error rate went to 100% for all endpoints touching that model",
        "resolved_by": "Added the column alias to the model. Deployed. Added model-schema parity check to CI.",
        "helpers": "Bob Martinez",
        "links": "",
    },
    {
        "title": "Dead letter queue silently full for three weeks",
        "description": "The DLQ alarm threshold was set to 10,000 messages. The queue hit 9,999 and stayed there. 9,999 failed payment notifications were never retried.",
        "discovered_by": "Finance noticed a gap in reconciliation reports",
        "resolved_by": "Drained and replayed the DLQ. Fixed the threshold. Issued manual notifications to affected users.",
        "helpers": "Julia Santos, George Nakamura",
        "links": "",
    },
    {
        "title": "Pagination off-by-one returned duplicate results",
        "description": "Used offset instead of cursor-based pagination. An off-by-one error caused the last item of every page to appear as the first item of the next.",
        "discovered_by": "A user noticed they kept seeing the same product at the top of each page",
        "resolved_by": "Switched to cursor-based pagination. Fixed existing API clients.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Background worker crashed silently on startup",
        "description": "An exception in the worker init was swallowed by a bare except clause. The worker appeared healthy but processed zero jobs for 72 hours.",
        "discovered_by": "Queue depth alert finally triggered after 3 days",
        "resolved_by": "Fixed the init error. Removed the bare except. Added startup self-test.",
        "helpers": "Evan Torres",
        "links": "",
    },
    {
        "title": "Deployed a dependency with a known CVE",
        "description": "Ran npm audit --production and ignored the output because it had too many warnings. One of them was critical. An attacker used it to read environment variables remotely.",
        "discovered_by": "Automated CVE scanner in CI finally wired up to block deploys",
        "resolved_by": "Patched the dependency. Rotated all env vars. Conducted breach investigation.",
        "helpers": "Security team",
        "links": "https://example.com/cve-incident",
    },
    {
        "title": "Read replica promoted without updating app config",
        "description": "Primary RDS instance had a hardware failure. The replica was promoted automatically. The app was still pointing to the old primary endpoint for 22 minutes.",
        "discovered_by": "Connection refused errors in all database queries",
        "resolved_by": "Updated the connection string. Redeployed. Added DNS-based failover.",
        "helpers": "Diana Patel, Hannah Osei",
        "links": "",
    },
    {
        "title": "Forgot to add an index on a foreign key",
        "description": "A new many-to-many relationship was added without indexing the join table. Fine in staging with 100 rows. In production with 8 million rows, every related query took 45 seconds.",
        "discovered_by": "Latency alerts across the board after midnight deploy",
        "resolved_by": "Added the index concurrently. Query time dropped from 45s to 4ms.",
        "helpers": "George Nakamura",
        "links": "",
    },
    {
        "title": "Health check endpoint was returning 200 for a crashed service",
        "description": "The health check just returned 200 OK without actually checking dependencies. The service was deadlocked but the load balancer kept sending it traffic.",
        "discovered_by": "Users reported intermittent errors for 6 hours before someone correlated it with the health check",
        "resolved_by": "Rewrote health check to actually probe DB, cache, and queue. Removed the deadlocked instance.",
        "helpers": "",
        "links": "",
    },
    {
        "title": "Webhook endpoint had no authentication",
        "description": "A third-party webhook endpoint was deployed without signature verification. Anyone who guessed the URL could trigger payment status updates.",
        "discovered_by": "Penetration test",
        "resolved_by": "Added HMAC signature verification. Audited webhook logs for unauthorized calls.",
        "helpers": "Julia Santos",
        "links": "",
    },
    {
        "title": "Auto-scaling group scaled to 0 during a traffic spike",
        "description": "A misconfigured scaling policy had a minimum instance count of 0. A deployment triggered a scale-in event at the same time as a traffic spike.",
        "discovered_by": "Site went completely down for 8 minutes",
        "resolved_by": "Set minimum instance count to 2. Investigated and fixed the policy logic.",
        "helpers": "Diana Patel",
        "links": "",
    },
    {
        "title": "Unescaped user input in email subject line caused bounces",
        "description": "A user put a newline character in the name field. The email library interpreted it as a header injection. The emails were rejected by every mail server.",
        "discovered_by": "Transactional email delivery rate dropped to 0%",
        "resolved_by": "Sanitized input. Resent affected emails manually.",
        "helpers": "Fiona Reyes",
        "links": "",
    },
    {
        "title": "Config service returned stale values after a cache bug",
        "description": "A cache invalidation bug caused the config service to return values from 3 weeks ago. Feature flags, rate limits, and A/B test assignments were all wrong.",
        "discovered_by": "A/B test results looked suspiciously good. Someone checked the actual config.",
        "resolved_by": "Flushed the cache. Fixed the invalidation logic. Added config audit logging.",
        "helpers": "Ivan Petrov, Charlie Kim",
        "links": "",
    },
    {
        "title": "Bulk update query missing WHERE clause",
        "description": "UPDATE users SET email_verified = false. No WHERE clause. All 340,000 users were unverified instantly.",
        "discovered_by": "Login failure rate hit 100% for users with email verification required",
        "resolved_by": "Set everyone back to verified via another bulk update (with a WHERE clause this time). Required DB change review process introduced.",
        "helpers": "Alice Chen",
        "links": "https://example.com/bulk-update-incident",
    },
]


def seed_database(db: Session) -> None:
    if db.query(models.User).count() > 0:
        return

    users = []
    for ud in _USERS:
        user = models.User(name=ud["name"], team=ud["team"], nickname=ud.get("nickname"))
        db.add(user)
        users.append(user)
    db.commit()
    for u in users:
        db.refresh(u)

    now = datetime.utcnow()
    rng = random.Random(42)

    # Spread 100 incidents over the past 18 months with varied user assignments
    days_range = 18 * 30
    templates = _INCIDENT_TEMPLATES
    for i in range(100):
        tmpl = templates[i % len(templates)]
        days_ago = rng.randint(1, days_range)
        occurred = now - timedelta(days=days_ago, hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
        incident = models.Incident(
            user_id=users[rng.randint(0, len(users) - 1)].id,
            title=tmpl["title"],
            description=tmpl["description"],
            discovered_by=tmpl["discovered_by"],
            resolved_by=tmpl["resolved_by"],
            helpers=tmpl["helpers"] or None,
            links=tmpl["links"] or None,
            occurred_at=occurred,
        )
        db.add(incident)
    db.commit()

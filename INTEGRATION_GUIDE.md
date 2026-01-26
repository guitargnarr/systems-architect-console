# Ibanista Tools Integration Guide

**Prepared for:** Benjamin Small, Ibanista
**Prepared by:** Matthew Scott
**Date:** January 26, 2026

---

## Overview

This guide explains how to integrate the Ibanista Tools prototype into your main website at ibanista.com.

**Live Prototype:** https://ibanista-tools.vercel.app
**Backend API:** https://systems-architect-console.onrender.com
**Admin Dashboard:** https://systems-architect-console.onrender.com/admin

---

## Integration Options

### Option 1: Subdomain (Recommended)

Create `tools.ibanista.com` pointing to the Vercel deployment.

**Steps:**
1. In your DNS provider, add a CNAME record:
   ```
   tools.ibanista.com → cname.vercel-dns.com
   ```
2. In Vercel dashboard → Project Settings → Domains → Add `tools.ibanista.com`
3. Vercel auto-provisions SSL certificate

**Pros:** Clean URL, full-page experience, SEO benefits
**Cons:** Requires DNS access

---

### Option 2: Iframe Embed

Embed the tools directly on an existing ibanista.com page.

**Code to add:**
```html
<iframe
  src="https://ibanista-tools.vercel.app"
  width="100%"
  height="900"
  frameborder="0"
  style="border: none; border-radius: 8px;"
  title="Ibanista Relocation Tools"
></iframe>
```

**Pros:** No DNS changes, quick to implement
**Cons:** Scroll issues possible, less SEO value

---

### Option 3: Link from Navigation

Add a navigation link to the standalone tools page.

**Add to main menu:**
```html
<a href="https://ibanista-tools.vercel.app" target="_blank">Free Tools</a>
```

**Or with button styling:**
```html
<a href="https://ibanista-tools.vercel.app"
   class="btn btn-primary"
   target="_blank">
  Try Our Free Calculator
</a>
```

**Pros:** Zero technical changes to main site
**Cons:** Opens new tab, users leave main domain

---

## Recommended Navigation Structure

### Main Navigation Bar

```
Logo | Services | About | Resources | Free Tools | Contact
                                         ↑
                                    NEW ADDITION
```

### Free Tools Dropdown (Optional)

```
Free Tools ▼
├── Budget Calculator
├── Region Finder Quiz
└── Newsletter Signup
```

**Direct links:**
- Budget Calculator: `https://ibanista-tools.vercel.app#calculator`
- Region Finder: `https://ibanista-tools.vercel.app#quiz`
- Newsletter: `https://ibanista-tools.vercel.app#newsletter`

---

## Homepage Call-to-Action Placement

### Hero Section CTA

Add below your main headline:

```html
<div class="hero-cta">
  <a href="https://ibanista-tools.vercel.app" class="btn-primary">
    Calculate Your Move →
  </a>
  <span class="cta-subtext">Free budget estimate in 30 seconds</span>
</div>
```

### Mid-Page Feature Block

```html
<section class="tools-promo">
  <h2>Plan Your Move to France</h2>
  <p>Use our free tools to estimate costs and find your perfect region.</p>

  <div class="tool-cards">
    <div class="card">
      <h3>💰 Budget Calculator</h3>
      <p>Compare UK vs France living costs</p>
      <a href="https://ibanista-tools.vercel.app#calculator">Try Now</a>
    </div>

    <div class="card">
      <h3>🗺️ Region Finder</h3>
      <p>Discover your ideal French destination</p>
      <a href="https://ibanista-tools.vercel.app#quiz">Take Quiz</a>
    </div>
  </div>
</section>
```

---

## Footer Integration

Add to existing footer:

```html
<div class="footer-tools">
  <h4>Free Resources</h4>
  <ul>
    <li><a href="https://ibanista-tools.vercel.app#calculator">Relocation Budget Calculator</a></li>
    <li><a href="https://ibanista-tools.vercel.app#quiz">Find Your French Region Quiz</a></li>
    <li><a href="https://ibanista-tools.vercel.app#newsletter">Newsletter Signup</a></li>
  </ul>
</div>
```

---

## Tracking & Analytics

### Google Analytics Event Tracking

Add to your GA4 configuration to track tool usage:

```javascript
// Track clicks to tools
document.querySelectorAll('a[href*="ibanista-tools.vercel.app"]').forEach(link => {
  link.addEventListener('click', () => {
    gtag('event', 'click', {
      'event_category': 'Tools',
      'event_label': link.textContent,
      'value': 1
    });
  });
});
```

### UTM Parameters

Use UTM parameters to track traffic source:

```
https://ibanista-tools.vercel.app?utm_source=ibanista&utm_medium=nav&utm_campaign=tools
https://ibanista-tools.vercel.app?utm_source=ibanista&utm_medium=hero&utm_campaign=calculator
https://ibanista-tools.vercel.app?utm_source=ibanista&utm_medium=footer&utm_campaign=quiz
```

---

## Lead Flow Summary

```
User visits ibanista.com
        ↓
Clicks "Free Tools" or CTA
        ↓
Uses Calculator or Quiz
        ↓
Submits email for results
        ↓
Lead captured in backend database
        ↓
Admin views at /admin dashboard
        ↓
Email sequence triggered (when SMTP configured)
        ↓
Follow-up call scheduled
```

---

## Admin Dashboard Access

**URL:** https://systems-architect-console.onrender.com/admin

**Features:**
- Total leads count
- Emails queued count
- Filter by source (calculator/quiz/newsletter)
- View full lead details
- Real-time updates

**No login required currently.** To add authentication, contact Matthew Scott.

---

## Backend API Endpoints

For developers integrating directly:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/leads` | GET | List all leads |
| `/api/leads` | POST | Create new lead |
| `/api/leads/{id}` | GET | Get lead details |
| `/api/stats` | GET | Dashboard statistics |
| `/health` | GET | API health check |

**Base URL:** `https://systems-architect-console.onrender.com`

---

## Email Configuration (Next Step)

To activate email sending, provide:

1. **Option A: SendGrid**
   - API Key
   - Verified sender email

2. **Option B: Mailchimp**
   - API Key
   - Audience ID
   - From email address

3. **Option C: SMTP**
   - Host, Port
   - Username, Password
   - From email address

Once provided, emails will send automatically on lead capture.

---

## Support

**Technical questions:** Matthew Scott
**Repository:** https://github.com/guitargnarr/systems-architect-console

---

## Quick Start Checklist

- [ ] Choose integration method (subdomain, iframe, or link)
- [ ] Add "Free Tools" to main navigation
- [ ] Add CTA button to homepage hero
- [ ] Add tools section to footer
- [ ] Configure UTM tracking
- [ ] Test lead capture flow end-to-end
- [ ] Provide email credentials for automation
- [ ] Review leads in admin dashboard

---

**Ready to launch.** The tools are production-ready and capturing leads now.

# Ibanista Tools Prototype vs Real Site Audit

**Date:** January 26, 2026
**Prototype:** https://ibanista-tools.vercel.app
**Real Site:** https://www.ibanista.com

---

## Executive Summary

The prototype captures core brand elements but **misses several key features** from the real Ibanista site that would improve authenticity and functionality.

| Category | Prototype | Real Site | Gap |
|----------|-----------|-----------|-----|
| Brand Colors | ✅ Matched | Navy + Teal | — |
| Hero Message | ✅ Matched | Same tagline | — |
| Navigation | ⚠️ Simplified | Full dropdown menus | Missing |
| Chatbot | ❌ Missing | Landbot "GET STARTED" | Critical |
| Trustpilot | ❌ Missing | 5-star reviews | High |
| Newsletter Popup | ❌ Missing | Modal with phone mockup | Medium |
| Phone Number | ✅ Present | +44 203 376 5117 | — |
| Social Links | ⚠️ Partial | 5 platforms | Missing some |
| Blog Section | ❌ Missing | "Latest on the Blog" | Medium |
| Power Hour CTA | ❌ Missing | Prominent section | High |
| Services Detail | ⚠️ Basic | 3 detailed cards | Could improve |

---

## Critical Gaps (Must Fix)

### 1. Missing Chatbot Widget
**Real site has:** Landbot integration with "GET STARTED" button in hero
**Prototype has:** Nothing

**Impact:** The real site's primary CTA is the chatbot. Our prototype sends users to tools, but there's no conversational entry point.

**Fix:** Add floating chat button or "GET STARTED" CTA that could:
- Link to HubSpot booking (already mentioned)
- Open a simple contact modal
- Future: Connect to AI chatbot (Phase 2)

---

### 2. Missing Trustpilot Integration
**Real site has:** "Trustpilot" badge with 5-star rating prominently displayed
**Prototype has:** Generic "Trustpilot" text in trust badges, no actual widget

**Impact:** Social proof is weaker. Trustpilot is a recognized trust signal.

**Fix:** Either:
- Embed actual Trustpilot widget (requires their account)
- Use screenshot/image of their Trustpilot rating
- Add "Rated Excellent on Trustpilot" with link

---

### 3. Missing Power Hour Section
**Real site has:** Dedicated "Power Hour" service - 1-hour consultation, prominently featured
**Prototype has:** No mention

**Impact:** This is a key revenue product. The real site has a full section for it.

**Fix:** Add Power Hour card to services section:
```
Power Hour - €149
1-hour strategy session with an expert
Get personalized advice on your move
[Book Now]
```

---

## High Priority Gaps

### 4. Newsletter Popup Style
**Real site has:** Modal popup with:
- iPhone mockup showing "IBANISTA Weekly"
- "Sign up to the Ibanista's newsletter"
- First name + Email fields
- "Read by 4,200+ future and current expats"

**Prototype has:** Simple inline newsletter section

**Recommendation:** Consider adding entry/exit popup for higher conversion

---

### 5. Navigation Structure
**Real site navigation:**
```
WHY IBANISTA ▼
  - About Us
  - How We Help
MONEY TRANSFER
LONG-TERM RENTALS
POWER HOUR
FREE RESOURCES ▼
  - Webinars
  - Guides
  - Articles
[Phone: +44 203 376 5117]
```

**Prototype navigation:**
```
Ibanista | [Phone] | [Visit ibanista.com]
```

**Recommendation:** Not critical since prototype is a tools page, but could add dropdown for "Our Services" linking to real site sections.

---

### 6. Blog/Content Section
**Real site has:** "THE LATEST ON THE BLOG" section with 3 article cards
**Prototype has:** None

**Impact:** Content marketing drives SEO and engagement

**Recommendation:** Add "Latest Resources" section pulling from ibanista.com/blog or linking to it

---

## Medium Priority Gaps

### 7. Social Media Links
**Real site has:** Instagram, Facebook, YouTube, Spotify, LinkedIn (5 platforms)
**Prototype has:** Instagram, Facebook, LinkedIn (3 platforms)

**Missing:** YouTube, Spotify (they have a podcast!)

---

### 8. "Why Choose Ibanista" Section
**Real site has:** 3 cards:
- "We started because we've been there"
- "We're a B-Corp certified company"
- "We're FCA regulated"

**Prototype has:** Similar but slightly different wording

**Note:** B-Corp certification is a differentiator - ensure this is highlighted

---

### 9. Testimonials Section
**Real site has:** "TRUSTED BY EXPATS FROM THE UK, THE US AND BEYOND" with named testimonials
**Prototype has:** None (correctly avoided fabrication per content rules)

**Recommendation:** Link to testimonials page or Trustpilot reviews instead of creating fake ones

---

## What Prototype Does BETTER

| Feature | Prototype | Real Site |
|---------|-----------|-----------|
| Interactive Calculator | ✅ Full featured | ❌ None |
| Region Finder Quiz | ✅ Full featured | ❌ None |
| Lead Capture Backend | ✅ Working API | ❌ Just forms |
| Admin Dashboard | ✅ Real-time stats | ❌ None visible |
| Mobile Responsiveness | ✅ Excellent | ✅ Good |
| Page Load Speed | ✅ Fast (Vercel) | ⚠️ Slower (Wix?) |

---

## Recommended Actions

### Immediate (1-2 hours)
1. [ ] Add "GET STARTED" or "Book Free Consultation" floating button
2. [ ] Add Trustpilot badge/link to trust section
3. [ ] Add YouTube and Spotify to social links
4. [ ] Add Power Hour mention in services

### Short-term (1 day)
5. [ ] Add newsletter popup on exit intent
6. [ ] Add "Latest Resources" section linking to blog
7. [ ] Improve "Why Choose" section with B-Corp mention

### Optional (if requested)
8. [ ] Match full navigation structure
9. [ ] Add testimonials section (linked, not fabricated)
10. [ ] Add Landbot or similar chatbot widget

---

## Brand Accuracy Check

| Element | Real Site | Prototype | Match? |
|---------|-----------|-----------|--------|
| Primary Navy | #32373c | #32373c | ✅ |
| Teal Accent | #14b8a6 | #14b8a6 | ✅ |
| Gold/Orange | #e9a235 | #e9a235 | ✅ |
| Logo | IBANISTA wordmark | IBANISTA wordmark | ✅ |
| Tagline | "Your move to France, the calm, confident version" | Same | ✅ |
| Phone | +44 203 376 5117 | +44 203 376 5117 | ✅ |
| Address | 4th Floor Silverstream House... | Same | ✅ |

**Brand accuracy: 100%** - Colors, messaging, and contact info match perfectly.

---

## Technical Comparison

| Metric | Prototype | Real Site |
|--------|-----------|-----------|
| Platform | Vercel (React) | Wix (likely) |
| Load Time | ~1.5s | ~3-4s |
| Mobile Score | 95+ | ~80 |
| Interactive Tools | 3 | 0 |
| Lead Capture | API-backed | Form only |
| Analytics | Ready for GA4 | HubSpot |

---

## Conclusion

**Prototype strengths:**
- Interactive tools (unique differentiator)
- Fast, modern stack
- Working lead capture with admin dashboard
- Accurate branding

**Prototype gaps:**
- Missing chatbot/consultation CTA
- No Trustpilot widget
- No Power Hour product
- Simplified navigation

**Priority fix:** Add "Book Free Consultation" button linking to HubSpot scheduler - this matches the real site's primary conversion action.

---

**Prepared by:** Matthew Scott
**Date:** January 26, 2026

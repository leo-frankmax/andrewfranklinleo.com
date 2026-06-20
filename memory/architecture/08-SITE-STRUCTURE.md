# Site Structure

SharePoint hierarchy mapping with complete directory tree and URL structure.

## SharePoint → System Mapping

| SharePoint | System | URL Pattern |
|------------|--------|-------------|
| Web Application | Conglomerate | `/` (root) |
| Site Collection | Group | `/{group}/` |
| Site | Venture | `/{group}/{venture}/` |
| Sub-site | Offering | `/{group}/{venture}/{offering}/` |

## URL Structure

```
https://andrewfranklinleo.com/
├── /                                          # Conglomerate portal
├── /frankmax/                                 # Group landing
│   ├── /frankmax/frankmax-talent/             # Venture
│   │   ├── /frankmax/frankmax-talent/executive-search/
│   │   ├── /frankmax/frankmax-talent/workforce-management/
│   │   ├── /frankmax/frankmax-talent/talent-intelligence/
│   │   └── /frankmax/frankmax-talent/career-development/
│   ├── /frankmax/frankmax-learning/
│   │   ├── /frankmax/frankmax-learning/universities/
│   │   ├── /frankmax/frankmax-learning/academies/
│   │   ├── /frankmax/frankmax-learning/certifications/
│   │   ├── /frankmax/frankmax-learning/skill-development/
│   │   └── /frankmax/frankmax-learning/lifelong-learning/
│   ├── /frankmax/frankmax-consulting/
│   ├── /frankmax/frankmax-digital/
│   ├── /frankmax/frankmax-leadership/
│   ├── /frankmax/frankmax-research/
│   └── /frankmax/frankmax-workforce-solutions/
│
├── /virginbay/                                # Group landing
│   ├── /virginbay/virginbay-marketplace/
│   │   ├── /virginbay/virginbay-marketplace/consumer-commerce/
│   │   ├── /virginbay/virginbay-marketplace/b2b-commerce/
│   │   ├── /virginbay/virginbay-marketplace/digital-commerce/
│   │   └── /virginbay/virginbay-marketplace/global-trade/
│   ├── /virginbay/virginbay-services/
│   ├── /virginbay/virginbay-logistics/
│   ├── /virginbay/virginbay-financial-services/
│   ├── /virginbay/virginbay-ventures/
│   ├── /virginbay/virginbay-global-trade/
│   └── /virginbay/virginbay-innovation-markets/
│
├── /glosbe/                                   # Group landing
│   ├── /glosbe/glosbe-communities/
│   ├── /glosbe/glosbe-collaboration/
│   ├── /glosbe/glosbe-civic-networks/
│   ├── /glosbe/glosbe-media/
│   ├── /glosbe/glosbe-social-impact/
│   ├── /glosbe/glosbe-knowledge-networks/
│   └── /glosbe/glosbe-community-development/
│
├── /crenza/                                   # Group landing
│   ├── /crenza/crenza-wealth/
│   ├── /crenza/crenza-investments/
│   ├── /crenza/crenza-real-assets/
│   ├── /crenza/crenza-intellectual-capital/
│   ├── /crenza/crenza-trust-services/
│   ├── /crenza/crenza-infrastructure/
│   └── /crenza/crenza-strategic-holdings/
│
├── /leo-technologies/                         # Strategic vertical
├── /leo-capital/                              # Strategic vertical
├── /leo-ventures/                             # Strategic vertical
├── /leo-institute/                            # Strategic vertical
├── /leo-foundation/                           # Strategic vertical
└── /leo-global-governance-council/            # Strategic vertical
```

## Complete Directory Tree

```
sites/leo-global-holdings/
├── index.html                                # Conglomerate home
├── _conglomerate.json                        # Conglomerate metadata
│
├── frankmax/
│   ├── index.html                            # Group home
│   ├── _group.json
│   │
│   ├── frankmax-talent/
│   │   ├── index.html                        # Venture home
│   │   ├── _venture.json
│   │   ├── executive-search/
│   │   │   ├── index.html                    # Offering page
│   │   │   └── _offering.json
│   │   ├── workforce-management/
│   │   │   ├── index.html
│   │   │   └── _offering.json
│   │   ├── talent-intelligence/
│   │   │   ├── index.html
│   │   │   └── _offering.json
│   │   └── career-development/
│   │       ├── index.html
│   │       └── _offering.json
│   │
│   ├── frankmax-learning/
│   │   ├── index.html
│   │   ├── _venture.json
│   │   ├── universities/
│   │   │   ├── index.html
│   │   │   └── _offering.json
│   │   ├── academies/
│   │   ├── certifications/
│   │   ├── skill-development/
│   │   └── lifelong-learning/
│   │
│   ├── frankmax-consulting/
│   ├── frankmax-digital/
│   ├── frankmax-leadership/
│   ├── frankmax-research/
│   └── frankmax-workforce-solutions/
│
├── virginbay/
│   ├── index.html
│   ├── _group.json
│   ├── virginbay-marketplace/
│   │   ├── index.html
│   │   ├── _venture.json
│   │   ├── consumer-commerce/
│   │   ├── b2b-commerce/
│   │   ├── digital-commerce/
│   │   └── global-trade/
│   ├── virginbay-services/
│   ├── virginbay-logistics/
│   ├── virginbay-financial-services/
│   ├── virginbay-ventures/
│   ├── virginbay-global-trade/
│   └── virginbay-innovation-markets/
│
├── glosbe/
│   ├── index.html
│   ├── _group.json
│   ├── glosbe-communities/
│   ├── glosbe-collaboration/
│   ├── glosbe-civic-networks/
│   ├── glosbe-media/
│   ├── glosbe-social-impact/
│   ├── glosbe-knowledge-networks/
│   └── glosbe-community-development/
│
├── crenza/
│   ├── index.html
│   ├── _group.json
│   ├── crenza-wealth/
│   ├── crenza-investments/
│   ├── crenza-real-assets/
│   ├── crenza-intellectual-capital/
│   ├── crenza-trust-services/
│   ├── crenza-infrastructure/
│   └── crenza-strategic-holdings/
│
├── leo-technologies/
├── leo-capital/
├── leo-ventures/
├── leo-institute/
├── leo-foundation/
└── leo-global-governance-council/
```

## Page Template Mapping

| Level | Template | Key Content |
|-------|----------|-------------|
| Conglomerate | `conglomerate-home.html` | Mission, Vision, Groups grid, Ecosystem flow diagram |
| Group | `group-landing.html` | Group mission, Ventures grid, Stakeholders, Cross-ecosystem role |
| Venture | `venture-landing.html` | Venture mission, Offerings grid, Industry, Revenue model |
| Offering | `offering-landing.html` | Description, Functions, Benefits, Use cases, Related, CTA |

## Global Navigation Structure

```json
{
  "home": { "label": "Home", "url": "/" },
  "groups": [
    {
      "label": "Frankmax",
      "url": "/frankmax/",
      "mission": "Empowering Every Professional",
      "ventures": [
        {
          "label": "Frankmax Talent",
          "url": "/frankmax/frankmax-talent/",
          "offerings": [
            { "label": "Executive Search", "url": "/frankmax/frankmax-talent/executive-search/" },
            { "label": "Workforce Management", "url": "/frankmax/frankmax-talent/workforce-management/" }
          ]
        }
      ]
    }
  ],
  "strategic_verticals": [
    { "label": "Leo Technologies", "url": "/leo-technologies/" },
    { "label": "Leo Capital", "url": "/leo-capital/" },
    { "label": "Leo Ventures", "url": "/leo-ventures/" },
    { "label": "Leo Institute", "url": "/leo-institute/" },
    { "label": "Leo Foundation", "url": "/leo-foundation/" },
    { "label": "Leo Global Governance Council", "url": "/leo-global-governance-council/" }
  ]
}
```

## Breadcrumb Pattern

```
Home > {Group} > {Venture} > {Offering}

Example:
Home > Frankmax > Frankmax Talent > Executive Search
Home > Virginbay > Virginbay Marketplace > Consumer Commerce
Home > Glosbe > Glosbe Communities > Professional Networks
Home > Crenza > Crenza Wealth > Family Offices
```

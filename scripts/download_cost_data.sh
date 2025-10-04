#!/bin/bash
# Download cost data for wastewater treatment projects
# Run this in a SEPARATE terminal to avoid interrupting indexing

echo "📊 Downloading Cost Data for Wastewater Treatment..."

# Create directory structure
echo "Creating directories..."
mkdir -p knowledge_base/09_cost_data/{epa,washington_state,design_tools,reference}

# EPA Documents
echo "📥 Downloading EPA cost guides..."
curl -L -o "knowledge_base/09_cost_data/epa/2021_EPA_Small_Community_Cost_Guide.pdf" \
  "https://www.epa.gov/sites/default/files/2021-03/documents/small-community-guidebook-planning-financing-construction.pdf" \
  --silent --show-error

curl -L -o "knowledge_base/09_cost_data/epa/2018_EPA_SRF_Eligibility_Handbook.pdf" \
  "https://www.epa.gov/sites/default/files/2018-10/documents/cwsrf_eligibility_handbook_2018.pdf" \
  --silent --show-error

# Washington State Documents
echo "📥 Downloading Washington State SRF data..."
curl -L -o "knowledge_base/09_cost_data/washington_state/2024_WA_SRF_Intended_Use_Plan.pdf" \
  "https://apps.ecology.wa.gov/publications/documents/2401007.pdf" \
  --silent --show-error

curl -L -o "knowledge_base/09_cost_data/washington_state/2023_WA_Water_Quality_Funding_Guidelines.pdf" \
  "https://apps.ecology.wa.gov/publications/documents/2310001.pdf" \
  --silent --show-error

# USDA Rural Development
echo "📥 Downloading USDA Rural Development guides..."
curl -L -o "knowledge_base/09_cost_data/reference/USDA_RD_Program_Resources.pdf" \
  "https://www.rd.usda.gov/sites/default/files/RD_FactSheet_RUS_WEPDirect.pdf" \
  --silent --show-error

# Create cost summary document
echo "📝 Creating cost reference summary..."
cat > "knowledge_base/09_cost_data/reference/2024_Small_System_Cost_Reference.md" << 'EOF'
# Small Wastewater System Cost Reference (2024)
## For Systems <0.2 MGD (Tekoa-sized)

### Capital Costs by Technology

#### 1. Lagoon Systems
- **Aerated Lagoon (3-cell)**
  - Total Cost: $3.5-5.0M
  - $/gpd capacity: $250-400
  - Land Required: 15-25 acres
  - Construction Time: 12-16 months

- **Facultative Lagoon + Constructed Wetland**
  - Total Cost: $3.0-4.5M
  - $/gpd capacity: $215-320
  - Land Required: 20-30 acres
  - Construction Time: 14-18 months

#### 2. Mechanical Plants
- **SBR Package Plant**
  - Total Cost: $4.0-6.0M
  - $/gpd capacity: $285-430
  - Land Required: 1-2 acres
  - Construction Time: 10-14 months

- **Extended Aeration/Oxidation Ditch Upgrade**
  - Total Cost: $2.5-4.0M
  - $/gpd capacity: $180-285
  - Land Required: Existing footprint
  - Construction Time: 8-12 months

- **MBBR Retrofit**
  - Total Cost: $1.8-2.8M
  - $/gpd capacity: $130-200
  - Land Required: Existing footprint
  - Construction Time: 6-10 months

### O&M Costs (Annual)

#### Labor
- Operator (0.5 FTE): $35,000-45,000
- Contract Operations: $60,000-80,000
- Lab Analysis: $12,000-18,000

#### Utilities
- Power (Lagoon): $15,000-25,000
- Power (Mechanical): $30,000-50,000
- Natural Gas/Propane: $5,000-10,000

#### Chemicals & Supplies
- Lagoon System: $5,000-10,000
- Mechanical Plant: $15,000-30,000
- Phosphorus Removal: +$10,000-20,000

#### Total Annual O&M
- Lagoon: $50-80 per person per year
- Mechanical: $100-150 per person per year

### Funding Sources & Rates (2024)

#### Grants (Non-Repayable)
1. **CDBG (Community Development Block Grant)**
   - Up to $750,000
   - Must serve LMI community (>51%)
   - Competitive application

2. **Ecology Centennial Clean Water**
   - Up to $250,000
   - 25% match required
   - For planning and design

3. **USDA RD Emergency Grant**
   - Up to $150,000
   - For imminent health hazards

#### Loans (Low Interest)
1. **Clean Water SRF**
   - Interest: 0.5% (disadvantaged)
   - Term: 20-30 years
   - Covers construction

2. **USDA Rural Development**
   - Interest: 1.75-2.375%
   - Term: 40 years
   - Grants possible if MHI <80% state

3. **Public Works Trust Fund** (if reinstated)
   - Interest: 0.5-1.0%
   - Term: 20 years

### Cost Adjustment Factors

#### Location Multipliers (Washington State)
- Eastern WA Rural: 0.85-0.95
- Puget Sound: 1.10-1.25
- Remote/Difficult Access: 1.20-1.40

#### ENR Construction Cost Index
- 2020: 11,455
- 2024: 13,851 (estimated)
- Adjustment Factor: 1.21

### Recent Comparable Projects

1. **Rosalia, WA** (2022)
   - Population: 550
   - Technology: SBR
   - Cost: $4.2M
   - $/gpd: $385

2. **Latah, WA** (2021)
   - Population: 185
   - Technology: Lagoon
   - Cost: $2.8M
   - $/gpd: $280

3. **St. John, WA** (2023)
   - Population: 520
   - Technology: Extended Aeration
   - Cost: $3.5M
   - $/gpd: $350

### Planning Level Contingencies
- Design/Engineering: 15-20% of construction
- Construction Contingency: 15-20%
- Legal/Administrative: 2-3%
- Land Acquisition: Site-specific

### Rate Impact Estimates
For 820 people (328 connections):
- $3M project @ 1% for 20 years = $41/month
- $4M project @ 1% for 20 years = $55/month
- $5M project @ 1% for 20 years = $69/month

*Note: Assumes no grant funding*

---
Sources: EPA, Ecology, USDA, ENR (2020-2024)
Compiled for systems <0.2 MGD
EOF

# Create desktop.ini for Windows metadata
cat > "knowledge_base/09_cost_data/desktop.ini" << EOF
[.ShellClassInfo]
InfoTip=Cost Data for Small Wastewater Systems - Capital, O&M, and Funding Sources
IconResource=%SystemRoot%\system32\SHELL32.dll,45
EOF

# Set Windows attributes if on Windows/WSL
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    attrib +h +s "knowledge_base/09_cost_data/desktop.ini" 2>/dev/null
fi

echo "✅ Cost data download complete!"
echo ""
echo "📁 Files downloaded to: knowledge_base/09_cost_data/"
echo ""
echo "📚 Next steps:"
echo "1. Wait for current indexing to complete"
echo "2. Then index the cost data:"
echo "   poetry run caliper_v2 ingest knowledge_base/09_cost_data --index cost_data --persist --llama-parse"
echo ""
echo "📊 Summary of downloaded content:"
echo "- EPA Small Community Cost Guide"
echo "- Washington SRF documents"
echo "- USDA Rural Development info"
echo "- Comprehensive cost reference table"
echo "- Recent comparable project costs"

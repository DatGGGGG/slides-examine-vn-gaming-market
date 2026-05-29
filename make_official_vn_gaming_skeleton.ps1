Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RgbValue {
    param([int]$Red, [int]$Green, [int]$Blue)
    return $Red + ($Green -shl 8) + ($Blue -shl 16)
}

function Add-Rect {
    param(
        $Slide,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [int]$FillColor,
        [double]$Transparency = 0,
        [int]$LineVisible = 0,
        [int]$LineColor = 0,
        [double]$LineWeight = 1,
        [int]$Rounded = 0
    )

    $shapeType = if ($Rounded -eq 1) { 5 } else { 1 }
    $shape = $Slide.Shapes.AddShape($shapeType, $Left, $Top, $Width, $Height)
    $shape.Fill.ForeColor.RGB = $FillColor
    $shape.Fill.Transparency = $Transparency
    $shape.Line.Visible = $LineVisible
    if ($LineVisible -ne 0) {
        $shape.Line.ForeColor.RGB = $LineColor
        $shape.Line.Weight = $LineWeight
    }
    return $shape
}

function Add-Line {
    param(
        $Slide,
        [double]$X1,
        [double]$Y1,
        [double]$X2,
        [double]$Y2,
        [int]$Color,
        [double]$Weight = 1
    )

    $line = $Slide.Shapes.AddLine($X1, $Y1, $X2, $Y2)
    $line.Line.ForeColor.RGB = $Color
    $line.Line.Weight = $Weight
    return $line
}

function Add-TextBox {
    param(
        $Slide,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [string]$Text,
        [string]$FontName = "Aptos",
        [double]$FontSize = 18,
        [int]$Color = 0,
        [int]$Bold = 0,
        [int]$Alignment = 1,
        [double]$MarginLeft = 8,
        [double]$MarginRight = 8,
        [double]$MarginTop = 6,
        [double]$MarginBottom = 6
    )

    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    $shape.Line.Visible = 0
    $shape.Fill.Visible = 0
    $shape.TextFrame.MarginLeft = $MarginLeft
    $shape.TextFrame.MarginRight = $MarginRight
    $shape.TextFrame.MarginTop = $MarginTop
    $shape.TextFrame.MarginBottom = $MarginBottom
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.TextRange.Text = $Text
    $shape.TextFrame.TextRange.Font.Name = $FontName
    $shape.TextFrame.TextRange.Font.Size = $FontSize
    $shape.TextFrame.TextRange.Font.Bold = $Bold
    $shape.TextFrame.TextRange.Font.Color.RGB = $Color
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $Alignment
    return $shape
}

function Add-Footer {
    param(
        $Slide,
        [int]$SlideNumber,
        [int]$Red,
        [int]$TextColor
    )

    Add-Line -Slide $Slide -X1 0 -Y1 537 -X2 960 -Y2 537 -Color $Red -Weight 2.25 | Out-Null
    Add-TextBox -Slide $Slide -Left 36 -Top 506 -Width 500 -Height 20 -Text "VN Gaming Market Opportunity 2026 | Official deck skeleton" -FontName "Aptos" -FontSize 9.5 -Color $TextColor | Out-Null
    Add-TextBox -Slide $Slide -Left 884 -Top 504 -Width 40 -Height 20 -Text ([string]$SlideNumber) -FontName "Aptos" -FontSize 10 -Color $TextColor -Bold 1 -Alignment 3 | Out-Null
}

function Add-SectionDivider {
    param(
        $Slide,
        [string]$Part,
        [string]$Section,
        [string]$Message,
        [int]$Red,
        [int]$Maroon,
        [int]$Ink,
        [int]$Muted,
        [int]$Soft
    )

    Add-Rect -Slide $Slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor (Get-RgbValue 255 255 255) | Out-Null
    Add-Rect -Slide $Slide -Left 0 -Top 0 -Width 220 -Height 540 -FillColor $Red | Out-Null
    Add-Rect -Slide $Slide -Left 48 -Top 70 -Width 112 -Height 8 -FillColor (Get-RgbValue 255 230 230) | Out-Null
    Add-TextBox -Slide $Slide -Left 46 -Top 110 -Width 150 -Height 30 -Text $Part.ToUpperInvariant() -FontName "Aptos" -FontSize 12 -Color (Get-RgbValue 255 255 255) -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 254 -Top 118 -Width 600 -Height 56 -Text $Section -FontName "Aptos Display" -FontSize 28 -Color $Ink -Bold 1 | Out-Null
    Add-Rect -Slide $Slide -Left 256 -Top 196 -Width 560 -Height 144 -FillColor $Soft -Rounded 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 278 -Top 218 -Width 514 -Height 88 -Text $Message -FontName "Aptos" -FontSize 17 -Color $Ink | Out-Null
    Add-TextBox -Slide $Slide -Left 256 -Top 364 -Width 430 -Height 24 -Text "This section starts as a placeholder structure and will be populated slide by slide." -FontName "Aptos" -FontSize 11 -Color $Muted | Out-Null
    Add-Footer -Slide $Slide -SlideNumber $script:slideNumber -Red $Maroon -TextColor $Muted
}

function Add-SkeletonSlide {
    param(
        $Slide,
        [string]$Part,
        [string]$Section,
        [string]$Title,
        [string]$Purpose,
        [string]$Evidence,
        [string]$Visuals,
        [string]$Takeaway,
        [string]$ContinuationLabel,
        [int]$Red,
        [int]$Maroon,
        [int]$Ink,
        [int]$Muted,
        [int]$SoftRed,
        [int]$SoftGray,
        [int]$SoftAccent,
        [int]$Line
    )

    Add-Rect -Slide $Slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor (Get-RgbValue 255 255 255) | Out-Null
    Add-TextBox -Slide $Slide -Left 40 -Top 20 -Width 380 -Height 18 -Text "$Part > $Section" -FontName "Aptos" -FontSize 9.5 -Color $Red -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 38 -Top 42 -Width 690 -Height 40 -Text $Title -FontName "Aptos Display" -FontSize 23 -Color $Ink -Bold 1 | Out-Null
    if ($ContinuationLabel) {
        Add-Rect -Slide $Slide -Left 792 -Top 38 -Width 118 -Height 28 -FillColor $SoftAccent -Rounded 1 | Out-Null
        Add-TextBox -Slide $Slide -Left 800 -Top 43 -Width 100 -Height 18 -Text $ContinuationLabel -FontName "Aptos" -FontSize 10.5 -Color $Maroon -Bold 1 -Alignment 2 | Out-Null
    }
    Add-Line -Slide $Slide -X1 40 -Y1 86 -X2 920 -Y2 86 -Color $Line -Weight 0.9 | Out-Null

    Add-Rect -Slide $Slide -Left 40 -Top 106 -Width 430 -Height 118 -FillColor $SoftRed -Rounded 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 56 -Top 120 -Width 160 -Height 24 -Text "Objective / storyline" -FontName "Aptos" -FontSize 12 -Color $Red -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 54 -Top 148 -Width 398 -Height 60 -Text $Purpose -FontName "Aptos" -FontSize 14.5 -Color $Ink | Out-Null

    Add-Rect -Slide $Slide -Left 40 -Top 238 -Width 430 -Height 238 -FillColor $SoftGray -Rounded 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 56 -Top 252 -Width 150 -Height 24 -Text "Evidence to insert" -FontName "Aptos" -FontSize 12 -Color $Red -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 54 -Top 280 -Width 398 -Height 176 -Text $Evidence -FontName "Aptos" -FontSize 13 -Color $Ink | Out-Null

    Add-Rect -Slide $Slide -Left 492 -Top 106 -Width 428 -Height 176 -FillColor $SoftGray -Rounded 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 508 -Top 120 -Width 160 -Height 24 -Text "Suggested visual" -FontName "Aptos" -FontSize 12 -Color $Red -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 506 -Top 148 -Width 392 -Height 120 -Text $Visuals -FontName "Aptos" -FontSize 13 -Color $Ink | Out-Null

    Add-Rect -Slide $Slide -Left 492 -Top 298 -Width 428 -Height 178 -FillColor $SoftAccent -Rounded 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 508 -Top 312 -Width 150 -Height 24 -Text "Draft takeaway" -FontName "Aptos" -FontSize 12 -Color $Maroon -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left 506 -Top 340 -Width 392 -Height 118 -Text $Takeaway -FontName "Aptos" -FontSize 13.5 -Color $Ink | Out-Null

    Add-Footer -Slide $Slide -SlideNumber $script:slideNumber -Red $Maroon -TextColor $Muted
}

function New-SlideSpec {
    param(
        [string]$Part,
        [string]$Section,
        [string]$Title,
        [string]$Purpose,
        [string]$Evidence,
        [string]$Visuals,
        [string]$Takeaway,
        [int]$Count = 1
    )

    return [pscustomobject]@{
        Part = $Part
        Section = $Section
        Title = $Title
        Purpose = $Purpose
        Evidence = $Evidence
        Visuals = $Visuals
        Takeaway = $Takeaway
        Count = $Count
    }
}

$outputPath = Join-Path $PSScriptRoot "VN_Gaming_Market_Opportunity_2026_Official_Skeleton.pptx"

$red = Get-RgbValue 227 31 37
$maroon = Get-RgbValue 128 22 22
$ink = Get-RgbValue 67 67 67
$muted = Get-RgbValue 110 110 110
$softRed = Get-RgbValue 252 241 241
$softGray = Get-RgbValue 247 247 247
$softAccent = Get-RgbValue 250 244 239
$dividerSoft = Get-RgbValue 245 239 236
$line = Get-RgbValue 220 220 220

$slideSpecs = @(
    (New-SlideSpec -Part "Executive Summary" -Section "Executive Summary" -Title "Answer first: is Vietnam a 1-3 year sourcing opportunity?" -Purpose "Set up the investment answer in one slide before the evidence section begins." -Evidence "Placeholders:`n- One-sentence answer`n- 3 supporting proof points`n- 2 key risks`n- Recommendation for 2026 sourcing focus" -Visuals "Executive scorecard, demand vs. supply mini-chart, or yes/no recommendation panel." -Takeaway "Draft message: Vietnam likely offers an attractive near-term opportunity if demand readiness rises faster than supply of high-quality local games." -Count 1),
    (New-SlideSpec -Part "Executive Summary" -Section "Executive Summary" -Title "Implication for 2026 sourcing strategy" -Purpose "Translate the market answer into sourcing implications, target genres, and next-step decisions." -Evidence "Placeholders:`n- Which genres to prioritize`n- What to avoid`n- Type of studios to target`n- Strategic timing window" -Visuals "Priority matrix by genre and sourcing route." -Takeaway "Draft message: We should define a selective, evidence-led sourcing thesis instead of treating Vietnam as a broad market bet." -Count 1),

    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Demand-side Factors" -Title "Income per capita" -Purpose "Show whether rising spending power supports greater gaming demand in Vietnam." -Evidence "Insert from outline:`n- Current income per capita`n- Last 10 years trend, 2016-2025`n- Geo heatmap vs. peers`n- GDP sector distribution shift`n- Short conclusion" -Visuals "Line chart for 2016-2025, peer-country heatmap, stacked sector mix." -Takeaway "Draft message: Income growth expands the addressable audience for mobile and PC gaming, especially beyond entry-level spend." -Count 1),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Demand-side Factors" -Title "Demographics" -Purpose "Connect age structure, workforce scale, and digital-native cohorts to game demand potential." -Evidence "To fill later:`n- Population scale and growth`n- Age mix / gamer-relevant cohorts`n- Urban-rural split`n- Any 2026 implication for mid-core and casual demand" -Visuals "Population pyramid, age-band bars, or gamer-addressable cohort chart." -Takeaway "Draft message: Vietnam's demographic structure still supports broad gamer acquisition, but not all cohorts are equally monetizable." -Count 1),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Demand-side Factors" -Title "Mobile penetration and internet infrastructure" -Purpose "Test whether access conditions are strong enough to sustain mobile and PC engagement growth." -Evidence "To fill later:`n- Smartphone penetration`n- 4G/5G and broadband quality`n- Internet penetration`n- Time spent online / device behavior" -Visuals "Penetration trend lines, infrastructure benchmark table, coverage map." -Takeaway "Draft message: Access barriers appear low enough that content fit and monetization matter more than device availability." -Count 1),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Demand-side Factors" -Title "Government regulation and policy" -Purpose "Establish whether regulation is a growth enabler, a compliance burden, or both." -Evidence "To fill later:`n- Licensing process`n- Content restrictions`n- Foreign/local publisher considerations`n- Policy shifts affecting mobile and PC" -Visuals "Policy timeline, regulatory flowchart, risk matrix." -Takeaway "Draft message: Regulation shapes speed-to-market and portfolio construction, not just legal overhead." -Count 2),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Demand-side Factors" -Title "Social acceptance and gaming culture" -Purpose "Assess whether gaming is mainstream enough to support broader demand and deeper engagement." -Evidence "To fill later:`n- Public perception of gaming`n- Social acceptance by age or gender`n- Esports / streamer influence`n- Time-spent and community signals" -Visuals "Culture signal dashboard, social trend examples, gamer-community map." -Takeaway "Draft message: Cultural normalization influences retention and monetization as much as raw player growth." -Count 3),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Demand-side Factors" -Title "Preference for domestic entertainment content" -Purpose "Determine whether locally resonant IP or cultural familiarity creates an edge for Vietnamese-made games." -Evidence "To fill later:`n- Evidence from entertainment consumption`n- Domestic vs. imported content preference`n- Relevance to game art/theme/story`n- Implication for Made in VN titles" -Visuals "Content-preference comparison, case examples, local-vs-global resonance ladder." -Takeaway "Draft message: Domestic affinity may not guarantee hits, but it can improve discoverability and emotional fit." -Count 3),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Supply-side Factors" -Title "Quality of Made in VN games and capability of VN studios" -Purpose "Evaluate whether local studios can deliver mid-core and casual titles that compete on quality." -Evidence "To fill later:`n- Representative local titles`n- Production quality benchmarks`n- LiveOps capability`n- Team maturity and specialization" -Visuals "Capability maturity ladder, benchmark gallery, studio landscape map." -Takeaway "Draft message: Supply quality is the gating factor; opportunity improves if leading studios can cross the quality threshold consistently." -Count 2),
    (New-SlideSpec -Part "Macro & Cultural Factors" -Section "Supply-side Factors" -Title "Perceived profitability in the VN market" -Purpose "Show whether developer and publisher economics make Vietnam worth prioritizing." -Evidence "To fill later:`n- Revenue pool attractiveness`n- UA efficiency or CAC signals`n- Monetization expectations`n- Views from local operators or publishers" -Visuals "Economics bridge, monetization benchmark chart, quote wall." -Takeaway "Draft message: Profitability perception affects how much serious studio talent stays focused on Vietnam rather than exporting globally." -Count 2),

    (New-SlideSpec -Part "Demand Analysis" -Section "Overall Demand" -Title "Historical overall demand" -Purpose "Measure the long-run size and growth of game demand in Vietnam across mobile and Steam-relevant PC demand." -Evidence "Insert from outline:`n- Downloads, DAU, revenue from 2010-2025`n- Sensor Tower mobile`n- Steam estimate for Vietnam`n- Commentary on major phases" -Visuals "Three-panel trend chart for downloads, DAU, and revenue." -Takeaway "Draft message: Demand trend should show whether Vietnam is still ramping structurally or maturing into a steadier market." -Count 1),
    (New-SlideSpec -Part "Demand Analysis" -Section "Overall Demand" -Title "Forecasted overall demand" -Purpose "Project the next 1-3 years of demand and tie the forecast back to macro conditions." -Evidence "Insert from outline:`n- Qualitative forecast with autoregression model`n- Confirmation or adjustment using macro and cultural factors" -Visuals "Historical + forecast line chart with assumption callouts." -Takeaway "Draft message: Forecast should separate baseline growth from upside driven by readiness factors." -Count 1),
    (New-SlideSpec -Part "Demand Analysis" -Section "Demand for Made in VN Games" -Title "Historical demand for Made in VN games" -Purpose "Test whether local games already have evidence of product-market fit in Vietnam." -Evidence "Insert from outline:`n- Downloads, DAU, revenue from 2010-2025`n- Mobile and Steam estimates`n- Data cleaning on identifying Made in VN titles" -Visuals "Demand trend plus title-level breakout or cohort examples." -Takeaway "Draft message: If local-game demand is rising faster than total demand, Vietnam becomes more attractive as a sourcing market rather than only a distribution market." -Count 1),
    (New-SlideSpec -Part "Demand Analysis" -Section "Demand for Made in VN Games" -Title "Forecasted demand for Made in VN games" -Purpose "Project whether local-title demand can outgrow the market over the next 1-3 years." -Evidence "Insert from outline:`n- Qualitative forecast with autoregression model`n- Confirmation or adjustment using the macro and cultural factors above" -Visuals "Forecast bridge from current demand to 2026-2028 opportunity." -Takeaway "Draft message: The core question is whether readiness for local titles compounds quickly enough to create a sourcing window." -Count 1),

    (New-SlideSpec -Part "Supply Analysis" -Section "Overall Supply" -Title "Historical overall supply" -Purpose "Show how many new games are entering Vietnam and whether supply is crowding the market." -Evidence "Insert from outline:`n- Mobile new releases on Vietnamese stores`n- Officially licensed games`n- Steam global new releases for reference`n- ABEI licensing crawl input" -Visuals "Supply trend line, licensed vs. total bars, reference panel for Steam." -Takeaway "Draft message: Rising supply alone is not enough; the key is whether quality supply is growing fast enough to absorb demand." -Count 1),
    (New-SlideSpec -Part "Supply Analysis" -Section "Overall Supply" -Title "Forecasted overall supply" -Purpose "Estimate the next 1-3 years of release volume and licensing activity." -Evidence "Insert from outline:`n- Qualitative forecast with autoregression model`n- Confirmation or adjustment using prior factors" -Visuals "Historical + forecast bars with annotation on regulatory or studio drivers." -Takeaway "Draft message: A moderate supply ramp may still leave room if demand and quality expectations grow faster." -Count 1),
    (New-SlideSpec -Part "Supply Analysis" -Section "Supply of Made in VN Games" -Title "Historical supply of Made in VN games" -Purpose "Measure whether Vietnamese studios have meaningfully scaled local output over time." -Evidence "Insert from outline:`n- Newly released Made in VN games on Vietnamese stores`n- Official licenses for Made in VN titles`n- Steam global releases from VN studios" -Visuals "Local supply trend, studio count trend, notable release examples." -Takeaway "Draft message: If local supply remains thin relative to demand potential, sourcing leverage improves." -Count 1),
    (New-SlideSpec -Part "Supply Analysis" -Section "Supply of Made in VN Games" -Title "Forecasted supply for Made in VN games" -Purpose "Project whether local output can fill the opportunity window quickly or slowly." -Evidence "Insert from outline:`n- Qualitative forecast with autoregression model`n- Confirmation or adjustment using studio capability and profitability perceptions" -Visuals "Supply forecast with scenarios: base, upside, constrained." -Takeaway "Draft message: Opportunity is strongest if local supply growth lags local demand growth for quality titles." -Count 1),

    (New-SlideSpec -Part "Demand-Supply Balance" -Section "Overall Demand-Supply Balance" -Title "Overall demand-supply balance" -Purpose "Synthesize whether Vietnam is becoming more crowded or more open at the market level." -Evidence "To fill later:`n- Demand vs. supply trend`n- Saturation or whitespace indicators`n- Implication for mobile and PC" -Visuals "Demand-supply gap chart, opportunity quadrant, or market heatmap." -Takeaway "Draft message: Opportunity depends on the size and persistence of the imbalance, not just on demand growth alone." -Count 1),
    (New-SlideSpec -Part "Demand-Supply Balance" -Section "Demand-Supply Balance for Made in VN Games" -Title "Demand-supply balance for Made in VN games" -Purpose "Answer the key sourcing question: is there an underserved space for high-quality local titles?" -Evidence "To fill later:`n- Local demand vs. local supply`n- Quality-adjusted gap`n- Genre-specific whitespace`n- 1-3 year timing view" -Visuals "Gap-to-opportunity bridge or genre whitespace matrix." -Takeaway "Draft message: The best sourcing case emerges when demand readiness outpaces the supply of credible Made in VN titles." -Count 1),

    (New-SlideSpec -Part "Conclusion" -Section "Conclusion" -Title "Conclusion: does Vietnam offer a sharp sourcing opportunity in 2026?" -Purpose "Wrap the deck with a direct answer, supporting logic, risks, and recommendation." -Evidence "Insert from outline:`n- Strong opportunity or not`n- Why demand is increasing and conditions are ready`n- Why supply stays low`n- Key challenge: development + LiveOps vs. international competition" -Visuals "Final recommendation page with confidence level, proof points, and next steps." -Takeaway "Draft message: The final call should clearly state whether Vietnam deserves focused sourcing attention in the next 1-3 years." -Count 1)
)

$ppt = $null
$presentation = $null
$script:slideNumber = 1

try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = -1

    $presentation = $ppt.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    # Cover slide
    $slide = $presentation.Slides.Add(1, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor (Get-RgbValue 255 255 255) | Out-Null
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 7 -FillColor $red | Out-Null
    Add-Rect -Slide $slide -Left 0 -Top 533 -Width 960 -Height 7 -FillColor $red | Out-Null
    Add-TextBox -Slide $slide -Left 52 -Top 72 -Width 180 -Height 24 -Text "OFFICIAL DECK SKELETON" -FontName "Aptos" -FontSize 12 -Color $red -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 50 -Top 112 -Width 650 -Height 86 -Text "Examining VN Gaming Market Opportunity 2026" -FontName "Aptos Display" -FontSize 30 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 52 -Top 214 -Width 640 -Height 56 -Text "Working hypothesis: there will be many advantages and opportunities in the Vietnam gaming market during the next 1-3 years, and we should capture them before the window closes." -FontName "Aptos" -FontSize 17 -Color $ink | Out-Null
    Add-Rect -Slide $slide -Left 52 -Top 312 -Width 854 -Height 106 -FillColor $softAccent -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 70 -Top 330 -Width 818 -Height 64 -Text "Scope`n- Vietnam gaming market only`n- Mobile and PC only`n- Mid-core and casual only; hypercasual and hybridcasual excluded" -FontName "Aptos" -FontSize 15 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 52 -Top 454 -Width 420 -Height 24 -Text "Palette learned from the supplied SVG template." -FontName "Aptos" -FontSize 11 -Color $muted | Out-Null
    Add-Footer -Slide $slide -SlideNumber $script:slideNumber -Red $maroon -TextColor $muted
    $script:slideNumber++

    # Section divider and content slides
    $parts = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($spec in $slideSpecs) {
        if (-not $parts.Contains($spec.Part)) {
            $divider = $presentation.Slides.Add($presentation.Slides.Count + 1, 12)
            $sectionMessage = switch ($spec.Part) {
                "Executive Summary" { "Lead with the answer, then use the rest of the deck to prove it." }
                "Macro & Cultural Factors" { "Establish the readiness conditions that shape demand and local content fit." }
                "Demand Analysis" { "Quantify how much player demand exists today and how it may evolve." }
                "Supply Analysis" { "Measure how much content is entering the market and where quality bottlenecks sit." }
                "Demand-Supply Balance" { "Synthesize the market gap into a sourcing opportunity lens." }
                "Conclusion" { "Close with a direct recommendation and the practical implication for 2026 sourcing." }
                default { "Section divider." }
            }
            Add-SectionDivider -Slide $divider -Part $spec.Part -Section $spec.Section -Message $sectionMessage -Red $red -Maroon $maroon -Ink $ink -Muted $muted -Soft $dividerSoft
            $parts.Add($spec.Part) | Out-Null
            $script:slideNumber++
        }

        for ($i = 1; $i -le $spec.Count; $i++) {
            $contentSlide = $presentation.Slides.Add($presentation.Slides.Count + 1, 12)
            $continuation = if ($spec.Count -gt 1) { "Placeholder $i/$($spec.Count)" } else { "" }
            $visualText = $spec.Visuals
            $takeawayText = $spec.Takeaway
            if ($spec.Count -gt 1) {
                switch ($i) {
                    1 {
                        $visualText = "$($spec.Visuals)`n`nUse this first slide for framing, definitions, or the headline evidence."
                        $takeawayText = "$($spec.Takeaway)`n`nUse this slide to land the first-order conclusion."
                    }
                    default {
                        $visualText = "$($spec.Visuals)`n`nUse this continuation to deepen examples, benchmarks, or risk nuance."
                        $takeawayText = "$($spec.Takeaway)`n`nUse this continuation to add nuance, exceptions, or implications."
                    }
                }
            }

            Add-SkeletonSlide -Slide $contentSlide -Part $spec.Part -Section $spec.Section -Title $spec.Title -Purpose $spec.Purpose -Evidence $spec.Evidence -Visuals $visualText -Takeaway $takeawayText -ContinuationLabel $continuation -Red $red -Maroon $maroon -Ink $ink -Muted $muted -SoftRed $softRed -SoftGray $softGray -SoftAccent $softAccent -Line $line
            $script:slideNumber++
        }
    }

    if (Test-Path -LiteralPath $outputPath) {
        Remove-Item -LiteralPath $outputPath -Force
    }

    $presentation.SaveAs($outputPath, 24)
    $presentation.Close()
    $ppt.Quit()

    Write-Output "Created: $outputPath"
    Write-Output "Slides: $($script:slideNumber - 1)"
}
finally {
    if ($presentation -ne $null) {
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) } catch {}
    }
    if ($ppt -ne $null) {
        try { $ppt.Quit() } catch {}
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

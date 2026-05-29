Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RgbValue {
    param(
        [int]$Red,
        [int]$Green,
        [int]$Blue
    )

    return $Red + ($Green -shl 8) + ($Blue -shl 16)
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
        [double]$FontSize = 20,
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
        [double]$Weight = 1.25
    )

    $line = $Slide.Shapes.AddLine($X1, $Y1, $X2, $Y2)
    $line.Line.ForeColor.RGB = $Color
    $line.Line.Weight = $Weight
    return $line
}

function Add-StatCard {
    param(
        $Slide,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [string]$Label,
        [string]$Value,
        [string]$Note,
        [int]$AccentColor,
        [int]$TextColor,
        [int]$MutedColor,
        [int]$CardColor
    )

    Add-Rect -Slide $Slide -Left $Left -Top $Top -Width $Width -Height $Height -FillColor $CardColor -Rounded 1 | Out-Null
    Add-Rect -Slide $Slide -Left ($Left + 14) -Top ($Top + 16) -Width 10 -Height ($Height - 32) -FillColor $AccentColor -Rounded 1 | Out-Null
    Add-TextBox -Slide $Slide -Left ($Left + 30) -Top ($Top + 12) -Width ($Width - 40) -Height 28 -Text $Label -FontName "Aptos" -FontSize 13 -Color $MutedColor -Bold 0 | Out-Null
    Add-TextBox -Slide $Slide -Left ($Left + 30) -Top ($Top + 36) -Width ($Width - 40) -Height 46 -Text $Value -FontName "Aptos Display" -FontSize 26 -Color $TextColor -Bold 1 | Out-Null
    Add-TextBox -Slide $Slide -Left ($Left + 30) -Top ($Top + 84) -Width ($Width - 40) -Height 40 -Text $Note -FontName "Aptos" -FontSize 10.5 -Color $MutedColor | Out-Null
}

$outputPath = Join-Path $PSScriptRoot "Vietnam_Demographics_Pilot_Deck.pptx"

$bg = Get-RgbValue 246 241 232
$paper = Get-RgbValue 255 251 245
$ink = Get-RgbValue 34 38 46
$muted = Get-RgbValue 102 99 92
$deepRed = Get-RgbValue 155 34 38
$gold = Get-RgbValue 210 160 70
$olive = Get-RgbValue 79 103 77
$teal = Get-RgbValue 50 108 112
$softRose = Get-RgbValue 240 223 219
$softGold = Get-RgbValue 242 234 212
$softOlive = Get-RgbValue 228 236 223
$softTeal = Get-RgbValue 221 233 232
$line = Get-RgbValue 208 199 186

$ppt = $null
$presentation = $null

try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = -1

    $presentation = $ppt.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    # Slide 1: Title
    $slide = $presentation.Slides.Add(1, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor $bg | Out-Null
    Add-Rect -Slide $slide -Left 620 -Top 0 -Width 340 -Height 540 -FillColor $deepRed | Out-Null
    Add-Rect -Slide $slide -Left 584 -Top 52 -Width 110 -Height 110 -FillColor $gold -Transparency 0.15 | Out-Null
    Add-Rect -Slide $slide -Left 760 -Top 300 -Width 132 -Height 132 -FillColor $gold -Transparency 0.08 -Rounded 1 | Out-Null

    Add-TextBox -Slide $slide -Left 64 -Top 70 -Width 500 -Height 44 -Text "Pilot Deck" -FontName "Aptos" -FontSize 15 -Color $deepRed -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 60 -Top 112 -Width 520 -Height 160 -Text "Overview of Vietnam demographics" -FontName "Aptos Display" -FontSize 28 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 60 -Top 278 -Width 470 -Height 98 -Text "A concise executive snapshot of population scale, age structure, urbanization, and key social signals. Figures are mostly for 2024 unless noted." -FontName "Aptos" -FontSize 17 -Color $muted | Out-Null
    Add-Line -Slide $slide -X1 64 -Y1 392 -X2 460 -Y2 392 -Color $line -Weight 1.1 | Out-Null
    Add-TextBox -Slide $slide -Left 60 -Top 404 -Width 500 -Height 32 -Text "Built on 19 May 2026 | For pilot discussion and refinement" -FontName "Aptos" -FontSize 11.5 -Color $muted | Out-Null

    Add-TextBox -Slide $slide -Left 676 -Top 90 -Width 180 -Height 70 -Text "Growing" -FontName "Aptos Display" -FontSize 26 -Color $paper -Bold 1 -Alignment 2 | Out-Null
    Add-TextBox -Slide $slide -Left 676 -Top 205 -Width 180 -Height 70 -Text "Aging" -FontName "Aptos Display" -FontSize 26 -Color $paper -Bold 1 -Alignment 2 | Out-Null
    Add-TextBox -Slide $slide -Left 676 -Top 320 -Width 180 -Height 70 -Text "Urbanizing" -FontName "Aptos Display" -FontSize 26 -Color $paper -Bold 1 -Alignment 2 | Out-Null

    # Slide 2: Snapshot
    $slide = $presentation.Slides.Add(2, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor $paper | Out-Null
    Add-TextBox -Slide $slide -Left 54 -Top 28 -Width 400 -Height 40 -Text "2024 demographic snapshot" -FontName "Aptos Display" -FontSize 25 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 56 -Top 66 -Width 710 -Height 26 -Text "Vietnam is now a very large population market with solid labor depth, but below-replacement fertility is becoming a central trend." -FontName "Aptos" -FontSize 13.5 -Color $muted | Out-Null

    Add-StatCard -Slide $slide -Left 56 -Top 118 -Width 196 -Height 138 -Label "Population (average, 2024)" -Value "101.3M" -Note "NSO estimate; up 1.03% from 2023." -AccentColor $deepRed -TextColor $ink -MutedColor $muted -CardColor $softRose
    Add-StatCard -Slide $slide -Left 270 -Top 118 -Width 196 -Height 138 -Label "Labor force (age 15+, 2024)" -Value "53.0M" -Note "Large workforce remains a key advantage." -AccentColor $gold -TextColor $ink -MutedColor $muted -CardColor $softGold
    Add-StatCard -Slide $slide -Left 484 -Top 118 -Width 196 -Height 138 -Label "Fertility rate (2024)" -Value "1.91" -Note "Children per woman; below replacement." -AccentColor $olive -TextColor $ink -MutedColor $muted -CardColor $softOlive
    Add-StatCard -Slide $slide -Left 698 -Top 118 -Width 196 -Height 138 -Label "Life expectancy (2024)" -Value "74.7" -Note "Years; unchanged into 2025 in NSO release." -AccentColor $teal -TextColor $ink -MutedColor $muted -CardColor $softTeal

    Add-Rect -Slide $slide -Left 56 -Top 294 -Width 838 -Height 164 -FillColor $bg -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 312 -Width 278 -Height 28 -Text "Why this matters" -FontName "Aptos Display" -FontSize 18 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 344 -Width 790 -Height 88 -Text "Vietnam has already crossed the 100 million threshold, which supports market scale, manufacturing depth, and a broad domestic consumer base. The strategic shift is no longer about whether the country is young, but how quickly it is moving from a demographic dividend phase toward an aging society." -FontName "Aptos" -FontSize 16 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 446 -Width 800 -Height 24 -Text "Sources: National Statistics Office of Vietnam releases on 2024 socio-economic conditions and 2024 intercensal population findings." -FontName "Aptos" -FontSize 10.5 -Color $muted | Out-Null

    # Slide 3: Age structure
    $slide = $presentation.Slides.Add(3, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor $bg | Out-Null
    Add-TextBox -Slide $slide -Left 54 -Top 28 -Width 430 -Height 40 -Text "Age structure is still favorable, but aging is accelerating" -FontName "Aptos Display" -FontSize 25 -Color $ink -Bold 1 | Out-Null

    $barLeft = 70
    $barTop = 152
    $barWidth = 560
    $barHeight = 42
    $childrenWidth = [math]::Round($barWidth * 0.2322, 0)
    $workingWidth = [math]::Round($barWidth * 0.6773, 0)
    $olderWidth = $barWidth - $childrenWidth - $workingWidth

    Add-Rect -Slide $slide -Left $barLeft -Top $barTop -Width $childrenWidth -Height $barHeight -FillColor $gold -Rounded 1 | Out-Null
    Add-Rect -Slide $slide -Left ($barLeft + $childrenWidth) -Top $barTop -Width $workingWidth -Height $barHeight -FillColor $olive | Out-Null
    Add-Rect -Slide $slide -Left ($barLeft + $childrenWidth + $workingWidth) -Top $barTop -Width $olderWidth -Height $barHeight -FillColor $deepRed -Rounded 1 | Out-Null

    Add-TextBox -Slide $slide -Left 70 -Top 108 -Width 580 -Height 26 -Text "Share of total population by age group, 2024" -FontName "Aptos" -FontSize 13 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 70 -Top 202 -Width 145 -Height 40 -Text "0-14 years`n23.2%" -FontName "Aptos Display" -FontSize 16 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 290 -Top 202 -Width 160 -Height 40 -Text "15-64 years`n67.7%" -FontName "Aptos Display" -FontSize 16 -Color $ink -Bold 1 -Alignment 2 | Out-Null
    Add-TextBox -Slide $slide -Left 502 -Top 202 -Width 140 -Height 40 -Text "65+ years`n9.1%" -FontName "Aptos Display" -FontSize 16 -Color $ink -Bold 1 -Alignment 3 | Out-Null

    Add-Rect -Slide $slide -Left 674 -Top 106 -Width 220 -Height 120 -FillColor $paper -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 690 -Top 122 -Width 190 -Height 28 -Text "Dependency ratio" -FontName "Aptos" -FontSize 13 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 686 -Top 148 -Width 196 -Height 38 -Text "47.7%" -FontName "Aptos Display" -FontSize 28 -Color $deepRed -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 690 -Top 188 -Width 188 -Height 28 -Text "Dependents per 100 working-age people." -FontName "Aptos" -FontSize 11 -Color $muted | Out-Null

    Add-Rect -Slide $slide -Left 56 -Top 284 -Width 838 -Height 182 -FillColor $paper -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 304 -Width 780 -Height 120 -Text "Vietnam still has a majority working-age population, which supports growth and labor supply. At the same time, the elderly share is climbing fast enough that population aging is now a near-term planning issue rather than a distant one. The working-age share shown here is inferred from age-band data: 100% minus 0-14 and 65+ shares." -FontName "Aptos" -FontSize 16 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 434 -Width 790 -Height 22 -Text "Sources: World Bank / UN Population Division age-band series for 2024; interpretation aligned with NSO population projection commentary." -FontName "Aptos" -FontSize 10.5 -Color $muted | Out-Null

    # Slide 4: Urbanization and labor
    $slide = $presentation.Slides.Add(4, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor $paper | Out-Null
    Add-TextBox -Slide $slide -Left 54 -Top 28 -Width 360 -Height 40 -Text "Urbanization is steady, not yet dominant" -FontName "Aptos Display" -FontSize 25 -Color $ink -Bold 1 | Out-Null

    Add-Rect -Slide $slide -Left 56 -Top 96 -Width 402 -Height 328 -FillColor $softTeal -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 74 -Top 118 -Width 350 -Height 28 -Text "Urban share of population" -FontName "Aptos" -FontSize 14 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 72 -Top 148 -Width 332 -Height 70 -Text "About 4 in 10" -FontName "Aptos Display" -FontSize 34 -Color $teal -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 74 -Top 228 -Width 344 -Height 94 -Text "A common global series places Vietnam's 2024 urban share at about 38.5%, while some NSO-based compilations show roughly 40.2%, depending on classification and update method." -FontName "Aptos" -FontSize 15 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 74 -Top 336 -Width 338 -Height 54 -Text "Bottom line: Vietnam is urbanizing quickly, but rural Vietnam still remains the majority setting." -FontName "Aptos" -FontSize 15 -Color $ink | Out-Null

    Add-Rect -Slide $slide -Left 492 -Top 96 -Width 402 -Height 328 -FillColor $bg -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 512 -Top 118 -Width 210 -Height 28 -Text "Labor market scale" -FontName "Aptos" -FontSize 14 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 510 -Top 154 -Width 180 -Height 40 -Text "51.9M employed" -FontName "Aptos Display" -FontSize 28 -Color $deepRed -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 512 -Top 198 -Width 334 -Height 70 -Text "The 2024 labor force aged 15 and over was nearly 53.0 million, with 51.9 million employed workers. This remains one of Vietnam's strongest demographic advantages." -FontName "Aptos" -FontSize 15 -Color $ink | Out-Null
    Add-Rect -Slide $slide -Left 512 -Top 286 -Width 154 -Height 90 -FillColor $softRose -Rounded 1 | Out-Null
    Add-Rect -Slide $slide -Left 682 -Top 286 -Width 154 -Height 90 -FillColor $softGold -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 522 -Top 300 -Width 132 -Height 24 -Text "Urban jobs" -FontName "Aptos" -FontSize 12 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 522 -Top 324 -Width 132 -Height 28 -Text "Unemployment" -FontName "Aptos Display" -FontSize 16 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 522 -Top 348 -Width 132 -Height 20 -Text "2.53% in 2024" -FontName "Aptos" -FontSize 11.5 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 692 -Top 300 -Width 132 -Height 24 -Text "Rural jobs" -FontName "Aptos" -FontSize 12 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 692 -Top 324 -Width 132 -Height 28 -Text "Unemployment" -FontName "Aptos Display" -FontSize 16 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 692 -Top 348 -Width 132 -Height 20 -Text "2.05% in 2024" -FontName "Aptos" -FontSize 11.5 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 72 -Top 452 -Width 800 -Height 24 -Text "Sources: NSO 2024 labor release; World Bank urban population series and NSO-based secondary compilations for the urban share." -FontName "Aptos" -FontSize 10.5 -Color $muted | Out-Null

    # Slide 5: Composition and social signals
    $slide = $presentation.Slides.Add(5, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor $bg | Out-Null
    Add-TextBox -Slide $slide -Left 54 -Top 28 -Width 400 -Height 40 -Text "Composition: diversity matters alongside scale" -FontName "Aptos Display" -FontSize 25 -Color $ink -Bold 1 | Out-Null

    Add-Rect -Slide $slide -Left 56 -Top 96 -Width 390 -Height 346 -FillColor $paper -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 116 -Width 340 -Height 28 -Text "Ethnic composition" -FontName "Aptos" -FontSize 14 -Color $muted | Out-Null
    Add-Rect -Slide $slide -Left 78 -Top 164 -Width 255 -Height 26 -FillColor $deepRed -Rounded 1 | Out-Null
    Add-Rect -Slide $slide -Left 333 -Top 164 -Width 45 -Height 26 -FillColor $gold -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 198 -Width 170 -Height 28 -Text "Kinh: 85.3%" -FontName "Aptos Display" -FontSize 18 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 248 -Top 198 -Width 170 -Height 28 -Text "Other ethnic groups: 14.7%" -FontName "Aptos Display" -FontSize 18 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 242 -Width 320 -Height 96 -Text "The 2019 census remains the best official baseline for ethnicity. Ethnic minority communities are disproportionately concentrated in the Northern Midlands and Mountain areas and the Central Highlands." -FontName "Aptos" -FontSize 15 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 76 -Top 350 -Width 320 -Height 44 -Text "Largest minority group in 2019: Tay (1.85 million)." -FontName "Aptos" -FontSize 14 -Color $muted | Out-Null

    Add-Rect -Slide $slide -Left 492 -Top 96 -Width 402 -Height 346 -FillColor $softOlive -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 512 -Top 116 -Width 250 -Height 28 -Text "Two social signals to watch" -FontName "Aptos" -FontSize 14 -Color $muted | Out-Null
    Add-TextBox -Slide $slide -Left 510 -Top 154 -Width 320 -Height 46 -Text "Sex ratio at birth: 111.4" -FontName "Aptos Display" -FontSize 24 -Color $olive -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 512 -Top 198 -Width 320 -Height 44 -Text "Boys per 100 girls in 2024, still materially above the biological norm." -FontName "Aptos" -FontSize 14.5 -Color $ink | Out-Null
    Add-Line -Slide $slide -X1 514 -Y1 258 -X2 842 -Y2 258 -Color $line -Weight 1.1 | Out-Null
    Add-TextBox -Slide $slide -Left 510 -Top 274 -Width 330 -Height 46 -Text "Fertility pressure is now national" -FontName "Aptos Display" -FontSize 24 -Color $deepRed -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 512 -Top 322 -Width 334 -Height 72 -Text "A 1.91 total fertility rate means the challenge is no longer concentrated only in richer East Asian peers. Vietnam is now moving into the same policy conversation." -FontName "Aptos" -FontSize 14.5 -Color $ink | Out-Null
    Add-TextBox -Slide $slide -Left 72 -Top 458 -Width 810 -Height 24 -Text "Sources: NSO 2024 population projection and vital-statistics summaries; NSO / UNFPA reporting from the 2019 census." -FontName "Aptos" -FontSize 10.5 -Color $muted | Out-Null

    # Slide 6: Takeaways
    $slide = $presentation.Slides.Add(6, 12)
    Add-Rect -Slide $slide -Left 0 -Top 0 -Width 960 -Height 540 -FillColor $paper | Out-Null
    Add-TextBox -Slide $slide -Left 54 -Top 30 -Width 420 -Height 40 -Text "What this means" -FontName "Aptos Display" -FontSize 25 -Color $ink -Bold 1 | Out-Null

    Add-Rect -Slide $slide -Left 56 -Top 96 -Width 838 -Height 314 -FillColor $bg -Rounded 1 | Out-Null
    Add-TextBox -Slide $slide -Left 82 -Top 118 -Width 754 -Height 52 -Text "1. Vietnam still benefits from demographic scale and a broad working-age base." -FontName "Aptos Display" -FontSize 20 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 82 -Top 168 -Width 754 -Height 52 -Text "2. The center of gravity is shifting from youth abundance toward aging management." -FontName "Aptos Display" -FontSize 20 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 82 -Top 218 -Width 754 -Height 52 -Text "3. Urbanization is meaningful but incomplete, so national strategy still has to work for both city and rural populations." -FontName "Aptos Display" -FontSize 20 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 82 -Top 268 -Width 754 -Height 52 -Text "4. Inclusion challenges remain visible in ethnicity, fertility, and sex-ratio trends." -FontName "Aptos Display" -FontSize 20 -Color $ink -Bold 1 | Out-Null
    Add-TextBox -Slide $slide -Left 82 -Top 332 -Width 760 -Height 42 -Text "Policy themes to watch: family support, healthy aging, urban infrastructure, labor productivity, and minority inclusion." -FontName "Aptos" -FontSize 16 -Color $deepRed | Out-Null

    Add-TextBox -Slide $slide -Left 56 -Top 438 -Width 840 -Height 56 -Text "Primary references used in this pilot deck: National Statistics Office of Vietnam 2024 socio-economic and population releases; NSO / UNFPA 2019 census publications; World Bank / UN Population Division age-structure series." -FontName "Aptos" -FontSize 12 -Color $muted | Out-Null

    if (Test-Path $outputPath) {
        Remove-Item -LiteralPath $outputPath -Force
    }

    $presentation.SaveAs($outputPath, 24)
    $presentation.Close()
    $ppt.Quit()

    Write-Output "Created: $outputPath"
}
finally {
    if ($presentation -ne $null) {
        try { [void][System.Runtime.Interopservices.Marshal]::ReleaseComObject($presentation) } catch {}
    }
    if ($ppt -ne $null) {
        try { $ppt.Quit() } catch {}
        try { [void][System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

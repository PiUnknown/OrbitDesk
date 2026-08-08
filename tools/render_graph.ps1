Add-Type -AssemblyName System.Drawing
$width = 1600; $height = 900
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.Clear([System.Drawing.Color]::White)
$font = New-Object System.Drawing.Font('Segoe UI', 18, [System.Drawing.FontStyle]::Regular)
$bold = New-Object System.Drawing.Font('Segoe UI', 20, [System.Drawing.FontStyle]::Bold)
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(55, 65, 81), 3)
$arrow = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(55, 65, 81), 3)
$arrow.EndCap = [System.Drawing.Drawing2D.LineCap]::Triangle
$fill = [System.Drawing.Brushes]::AliceBlue
$route = [System.Drawing.Brushes]::Honeydew
$warn = [System.Drawing.Brushes]::MistyRose
function Box($x, $y, $w, $h, $text, $brush, $fontToUse=$bold) {
  $rect = New-Object System.Drawing.Rectangle($x, $y, $w, $h)
  $graphics.FillRectangle($brush, $rect); $graphics.DrawRectangle($pen, $rect)
  $format = New-Object System.Drawing.StringFormat; $format.Alignment = 'Center'; $format.LineAlignment = 'Center'
  $rectF = New-Object System.Drawing.RectangleF([float]$x, [float]$y, [float]$w, [float]$h)
  $graphics.DrawString($text, $fontToUse, [System.Drawing.Brushes]::Black, $rectF, $format)
}
function Arrow($x1, $y1, $x2, $y2) { $graphics.DrawLine($arrow, $x1, $y1, $x2, $y2) }
Box 650 35 300 70 'START' $fill
Box 650 150 300 75 'TRIAGE' $route
Box 120 320 280 75 'RETRIEVAL' $fill
Box 500 320 280 75 'GENERATION' $fill
Box 880 320 300 75 'VERIFICATION' $route
Box 1260 320 260 75 'OUTPUT' $fill
Box 760 520 280 75 'REVISION' $warn
Box 120 520 280 75 'CLARIFICATION' $fill
Box 120 700 280 75 'ESCALATION' $warn
Box 1260 520 260 75 'OUT OF SCOPE' $warn
Box 1260 700 260 75 'SAFE FAILURE' $warn
Arrow 800 105 800 150; Arrow 800 225 260 320; Arrow 400 357 500 357; Arrow 780 357 880 357; Arrow 1180 357 1260 357
Arrow 1030 395 900 520; Arrow 900 595 1030 395; Arrow 1180 395 1390 520; Arrow 1390 595 1390 700
Arrow 650 187 260 520; Arrow 650 187 260 700
$graphics.DrawString('answerable', $font, [System.Drawing.Brushes]::DarkGreen, 420, 250)
$graphics.DrawString('pass', $font, [System.Drawing.Brushes]::DarkGreen, 1190, 330)
$graphics.DrawString('fail, retry < 1', $font, [System.Drawing.Brushes]::DarkRed, 900, 445)
$graphics.DrawString('clarification / escalation / out-of-scope', $font, [System.Drawing.Brushes]::DarkRed, 175, 430)
$graphics.DrawString('OrbitDesk Local-First Support Agent Network', $bold, [System.Drawing.Brushes]::Black, 465, 825)
$output = Join-Path $PSScriptRoot '..\docs\orbitdesk_graph.png'
$bitmap.Save((Resolve-Path (Join-Path $PSScriptRoot '..')).Path + '\docs\orbitdesk_graph.png', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
Write-Output $output

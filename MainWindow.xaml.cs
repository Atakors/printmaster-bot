using System;
using System.Globalization;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using Microsoft.Win32;
using PdfSharpCore.Drawing;
using PdfSharpCore.Pdf;

namespace PrintMasterA4
{
    public partial class MainWindow : Window
    {
        // =========================================================================
        // PHYSICAL TO PIXEL CONVERSIONS & CONSTANTS
        // =========================================================================
        private const double MmToDipFactor = 96.0 / 25.4;       // ~3.7795275 DIP per mm
        private const double DipToMmFactor = 25.4 / 96.0;
        private const double StandardA4WidthMm = 210.0;
        private const double StandardA4HeightMm = 297.0;

        // Active page setup
        private bool _isPortrait = true;
        private double _pageWidthMm = StandardA4WidthMm;
        private double _pageHeightMm = StandardA4HeightMm;

        // Page Margins (Paper Edge)
        private double _marginTopMm = 10.0;
        private double _marginBottomMm = 10.0;
        private double _marginLeftMm = 10.0;
        private double _marginRightMm = 10.0;

        // Image & Spacing state
        private BitmapSource? _sourceBitmap = null;
        private string? _sourceImagePath = null;
        private double _imageWidthMm = 50.0;   // 5.0 cm default
        private double _imageHeightMm = 50.0;  // 5.0 cm default
        private double _gapMm = 3.0;           // 3.0 mm default gap between images
        private double _aspectRatio = 1.0;
        private double _currentZoom = 0.85;

        private bool _isPosterMode = false;
        private bool _isUpdatingUi = false;

        public MainWindow()
        {
            InitializeComponent();
            UpdateA4Dimensions();
            LoadDefaultSampleImage();
            ApplyZoom(0.85);
        }

        // =========================================================================
        // DEFAULT DEMO STICKER
        // =========================================================================
        private void LoadDefaultSampleImage()
        {
            try
            {
                BitmapImage? bmp = null;

                // 1. Try loading embedded WPF resource
                try
                {
                    var sri = Application.GetResourceStream(new Uri("pack://application:,,,/Assets/sample_image.jpg", UriKind.Absolute));
                    if (sri != null)
                    {
                        using (var stream = sri.Stream)
                        {
                            bmp = new BitmapImage();
                            bmp.BeginInit();
                            bmp.StreamSource = stream;
                            bmp.CacheOption = BitmapCacheOption.OnLoad;
                            bmp.EndInit();
                            bmp.Freeze();
                        }
                    }
                }
                catch { }

                // 2. Try loading local file on disk
                if (bmp == null)
                {
                    string localPath = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "sample_image.jpg");
                    if (System.IO.File.Exists(localPath))
                    {
                        bmp = new BitmapImage();
                        bmp.BeginInit();
                        bmp.UriSource = new Uri(localPath, UriKind.Absolute);
                        bmp.CacheOption = BitmapCacheOption.OnLoad;
                        bmp.EndInit();
                        bmp.Freeze();
                    }
                }

                if (bmp != null)
                {
                    _sourceBitmap = bmp;
                    _aspectRatio = (double)bmp.PixelWidth / bmp.PixelHeight;
                    TxtImageFilename.Text = "sample_logo_a.jpg";
                    ImgThumbnail.Source = _sourceBitmap;

                    _imageWidthMm = 50.0;
                    _imageHeightMm = _imageWidthMm / _aspectRatio;

                    UpdateDimensionTextBoxes();
                    RefreshWorkspace();
                    return;
                }
            }
            catch
            {
                // Fall through to fallback procedural sticker
            }

            // Fallback sticker
            try
            {
                int size = 300;
                var dv = new DrawingVisual();
                using (var dc = dv.RenderOpen())
                {
                    dc.DrawRoundedRectangle(Brushes.White, new System.Windows.Media.Pen(new SolidColorBrush(System.Windows.Media.Color.FromRgb(203, 213, 225)), 2),
                        new Rect(15, 15, size - 30, size - 30), 40, 40);

                    var catBrush = new LinearGradientBrush(
                        System.Windows.Media.Color.FromRgb(125, 211, 252),
                        System.Windows.Media.Color.FromRgb(244, 114, 182),
                        45);

                    var earPath = new PathGeometry();
                    var fig1 = new PathFigure { StartPoint = new Point(70, 110) };
                    fig1.Segments.Add(new LineSegment(new Point(90, 40), true));
                    fig1.Segments.Add(new LineSegment(new Point(130, 95), true));
                    earPath.Figures.Add(fig1);

                    var fig2 = new PathFigure { StartPoint = new Point(170, 95) };
                    fig2.Segments.Add(new LineSegment(new Point(210, 40), true));
                    fig2.Segments.Add(new LineSegment(new Point(230, 110), true));
                    earPath.Figures.Add(fig2);
                    dc.DrawGeometry(catBrush, null, earPath);

                    dc.DrawEllipse(catBrush, null, new Point(150, 140), 75, 65);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromRgb(251, 168, 203)), null, new Point(95, 75), 12, 18);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromRgb(251, 168, 203)), null, new Point(205, 75), 12, 18);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromRgb(15, 23, 42)), null, new Point(120, 135), 14, 18);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromRgb(15, 23, 42)), null, new Point(180, 135), 14, 18);
                    dc.DrawEllipse(Brushes.White, null, new Point(116, 130), 5, 7);
                    dc.DrawEllipse(Brushes.White, null, new Point(176, 130), 5, 7);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromArgb(140, 244, 114, 182)), null, new Point(100, 155), 14, 8);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromArgb(140, 244, 114, 182)), null, new Point(200, 155), 14, 8);
                    dc.DrawEllipse(new SolidColorBrush(System.Windows.Media.Color.FromRgb(244, 63, 94)), null, new Point(150, 150), 4, 3);
                }

                var rtb = new RenderTargetBitmap(size, size, 96, 96, PixelFormats.Pbgra32);
                rtb.Render(dv);
                rtb.Freeze();

                _sourceBitmap = rtb;
                _aspectRatio = 1.0;
                TxtImageFilename.Text = "sticker_cute_cat.png";
                ImgThumbnail.Source = _sourceBitmap;

                UpdateDimensionTextBoxes();
                RefreshWorkspace();
            }
            catch { }
        }

        // =========================================================================
        // 1. PAGE SETUP & ORIENTATION
        // =========================================================================
        private void Orientation_Changed(object sender, RoutedEventArgs e)
        {
            if (!IsInitialized) return;
            _isPortrait = RbPortrait.IsChecked == true;
            UpdateA4Dimensions();
            RefreshWorkspace();
        }

        private void UpdateA4Dimensions()
        {
            _pageWidthMm = _isPortrait ? StandardA4WidthMm : StandardA4HeightMm;
            _pageHeightMm = _isPortrait ? StandardA4HeightMm : StandardA4WidthMm;

            PaperBorder.Width = _pageWidthMm * MmToDipFactor;
            PaperBorder.Height = _pageHeightMm * MmToDipFactor;
        }

        private void ApplyZoom(double zoom)
        {
            _currentZoom = Math.Max(0.3, Math.Min(2.0, zoom));
            if (CanvasScale != null)
            {
                CanvasScale.ScaleX = _currentZoom;
                CanvasScale.ScaleY = _currentZoom;
            }
            if (TxtZoomLevel != null)
            {
                TxtZoomLevel.Text = $"{(int)Math.Round(_currentZoom * 100)}%";
            }
        }

        private void BtnZoomIn_Click(object sender, RoutedEventArgs e) => ApplyZoom(_currentZoom + 0.1);
        private void BtnZoomOut_Click(object sender, RoutedEventArgs e) => ApplyZoom(_currentZoom - 0.1);
        private void BtnFitToScreen_Click(object sender, RoutedEventArgs e) => ApplyZoom(0.85);

        private void MenuZoomIn_Click(object sender, RoutedEventArgs e) => ApplyZoom(_currentZoom + 0.1);
        private void MenuZoomOut_Click(object sender, RoutedEventArgs e) => ApplyZoom(_currentZoom - 0.1);

        // =========================================================================
        // 2. IMAGE IMPORTING & DRAG-AND-DROP
        // =========================================================================
        private void BtnBrowse_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new OpenFileDialog
            {
                Filter = "Image Files (*.png;*.jpg;*.jpeg;*.bmp;*.webp)|*.png;*.jpg;*.jpeg;*.bmp;*.webp|All Files (*.*)|*.*",
                Title = "Select Image"
            };

            if (dlg.ShowDialog() == true)
            {
                LoadImageFromFile(dlg.FileName);
            }
        }

        private void Window_DragOver(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
                e.Handled = true;
            }
            else
            {
                e.Effects = DragDropEffects.None;
            }
        }

        private void Window_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                if (files != null && files.Length > 0)
                {
                    string file = files[0];
                    string ext = System.IO.Path.GetExtension(file).ToLowerInvariant();
                    if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".bmp" || ext == ".webp")
                    {
                        LoadImageFromFile(file);
                    }
                }
            }
        }

        private void LoadImageFromFile(string filePath)
        {
            try
            {
                _sourceImagePath = filePath;
                var bmp = new BitmapImage();
                bmp.BeginInit();
                bmp.UriSource = new Uri(_sourceImagePath);
                bmp.CacheOption = BitmapCacheOption.OnLoad;
                bmp.EndInit();
                bmp.Freeze();

                _sourceBitmap = bmp;
                _aspectRatio = (double)bmp.PixelWidth / bmp.PixelHeight;

                TxtImageFilename.Text = System.IO.Path.GetFileName(_sourceImagePath);
                ImgThumbnail.Source = _sourceBitmap;

                _imageWidthMm = 50.0;
                _imageHeightMm = _imageWidthMm / _aspectRatio;

                UpdateDimensionTextBoxes();
                RefreshWorkspace();
                TxtStatus.Text = "Image loaded successfully.";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Could not load image: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        // =========================================================================
        // 3. OPERATION MODE SWITCHING
        // =========================================================================
        private void BtnSelectModeDuplicator_Click(object sender, RoutedEventArgs e)
        {
            _isPosterMode = false;
            BorderModeDuplicator.Background = new SolidColorBrush(System.Windows.Media.Color.FromRgb(240, 247, 255));
            BorderModeDuplicator.BorderBrush = new SolidColorBrush(System.Windows.Media.Color.FromRgb(37, 99, 235));
            BorderModeDuplicator.BorderThickness = new Thickness(1.5);
            TxtModeDuplicator.Foreground = new SolidColorBrush(System.Windows.Media.Color.FromRgb(30, 64, 175));
            TxtModeDuplicator.FontWeight = FontWeights.SemiBold;

            BorderModePoster.Background = Brushes.White;
            BorderModePoster.BorderBrush = new SolidColorBrush(System.Windows.Media.Color.FromRgb(226, 232, 240));
            BorderModePoster.BorderThickness = new Thickness(1);
            TxtModePoster.Foreground = new SolidColorBrush(System.Windows.Media.Color.FromRgb(100, 116, 139));
            TxtModePoster.FontWeight = FontWeights.Normal;

            PanelDuplicatorOptions.Visibility = Visibility.Visible;
            PanelPosterOptions.Visibility = Visibility.Collapsed;
            RefreshWorkspace();
        }

        private void BtnSelectModePoster_Click(object sender, RoutedEventArgs e)
        {
            _isPosterMode = true;
            BorderModePoster.Background = new SolidColorBrush(System.Windows.Media.Color.FromRgb(240, 247, 255));
            BorderModePoster.BorderBrush = new SolidColorBrush(System.Windows.Media.Color.FromRgb(37, 99, 235));
            BorderModePoster.BorderThickness = new Thickness(1.5);
            TxtModePoster.Foreground = new SolidColorBrush(System.Windows.Media.Color.FromRgb(30, 64, 175));
            TxtModePoster.FontWeight = FontWeights.SemiBold;

            BorderModeDuplicator.Background = Brushes.White;
            BorderModeDuplicator.BorderBrush = new SolidColorBrush(System.Windows.Media.Color.FromRgb(226, 232, 240));
            BorderModeDuplicator.BorderThickness = new Thickness(1);
            TxtModeDuplicator.Foreground = new SolidColorBrush(System.Windows.Media.Color.FromRgb(100, 116, 139));
            TxtModeDuplicator.FontWeight = FontWeights.Normal;

            PanelDuplicatorOptions.Visibility = Visibility.Collapsed;
            PanelPosterOptions.Visibility = Visibility.Visible;
            RefreshWorkspace();
        }

        private void PosterPresetButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && btn.Tag is string tag)
            {
                var parts = tag.Split(',');
                if (parts.Length == 2 && int.TryParse(parts[0], out int c) && int.TryParse(parts[1], out int r))
                {
                    _isUpdatingUi = true;
                    TxtPosterCols.Text = c.ToString();
                    TxtPosterRows.Text = r.ToString();
                    _isUpdatingUi = false;
                    RefreshWorkspace();
                }
            }
        }

        private void BtnPosterColsUp_Click(object sender, RoutedEventArgs e)
        {
            if (int.TryParse(TxtPosterCols.Text, out int c))
            {
                TxtPosterCols.Text = Math.Min(12, c + 1).ToString();
            }
        }

        private void BtnPosterColsDown_Click(object sender, RoutedEventArgs e)
        {
            if (int.TryParse(TxtPosterCols.Text, out int c))
            {
                TxtPosterCols.Text = Math.Max(1, c - 1).ToString();
            }
        }

        private void BtnPosterRowsUp_Click(object sender, RoutedEventArgs e)
        {
            if (int.TryParse(TxtPosterRows.Text, out int r))
            {
                TxtPosterRows.Text = Math.Min(12, r + 1).ToString();
            }
        }

        private void BtnPosterRowsDown_Click(object sender, RoutedEventArgs e)
        {
            if (int.TryParse(TxtPosterRows.Text, out int r))
            {
                TxtPosterRows.Text = Math.Max(1, r - 1).ToString();
            }
        }

        private void BtnPosterOverlapUp_Click(object sender, RoutedEventArgs e)
        {
            string clean = TxtPosterOverlapMm.Text.Replace("mm", "").Trim();
            if (double.TryParse(clean, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double ov))
            {
                TxtPosterOverlapMm.Text = $"{Math.Min(40, ov + 1):F0} mm";
            }
        }

        private void BtnPosterOverlapDown_Click(object sender, RoutedEventArgs e)
        {
            string clean = TxtPosterOverlapMm.Text.Replace("mm", "").Trim();
            if (double.TryParse(clean, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double ov))
            {
                TxtPosterOverlapMm.Text = $"{Math.Max(0, ov - 1):F0} mm";
            }
        }

        private void BtnPosterOverlapPreset_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && btn.Tag is string tag)
            {
                TxtPosterOverlapMm.Text = $"{tag} mm";
            }
        }

        private void BtnBatchCopiesUp_Click(object sender, RoutedEventArgs e)
        {
            int current = int.TryParse(TxtTotalBatchCopies.Text, out int c) ? c : 0;
            int step = current >= 100 ? 50 : (current >= 20 ? 10 : 5);
            TxtTotalBatchCopies.Text = (current + step).ToString();
        }

        private void BtnBatchCopiesDown_Click(object sender, RoutedEventArgs e)
        {
            int current = int.TryParse(TxtTotalBatchCopies.Text, out int c) ? c : 0;
            int step = current > 100 ? 50 : (current > 20 ? 10 : 5);
            TxtTotalBatchCopies.Text = Math.Max(0, current - step).ToString();
        }

        private void BtnBatchPreset_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && btn.Tag is string tag)
            {
                TxtTotalBatchCopies.Text = tag;
            }
        }

        // =========================================================================
        // 4. PRESETS: STANDARD CARD/PHOTO SIZES & QUICK LAYOUTS
        // =========================================================================
        private void CmbStandardPresets_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (!IsInitialized || _sourceBitmap == null || CmbStandardPresets.SelectedIndex <= 0) return;

            switch (CmbStandardPresets.SelectedIndex)
            {
                case 1: SetDimensions(35, 45); break;     // Passport
                case 2: SetDimensions(51, 51); break;     // US Visa
                case 3: SetDimensions(85, 55); break;     // Business Card
                case 4: SetDimensions(85.6, 54); break;   // ID Badge
                case 5: SetDimensions(105, 148); break;   // A6 Postcard
                case 6: SetDimensions(148, 210); break;   // A5 Flyer
                case 7: SetDimensions(70, 70); break;     // Polaroid Sticker
            }
        }

        private void SetDimensions(double wMm, double hMm)
        {
            _imageWidthMm = wMm;
            _imageHeightMm = hMm;
            _isUpdatingUi = true;
            ChkLockRatio.IsChecked = false;
            TxtWidthCm.Text = $"{(_imageWidthMm / 10.0):F1} cm";
            TxtHeightCm.Text = $"{(_imageHeightMm / 10.0):F1} cm";
            _isUpdatingUi = false;

            RefreshWorkspace();
        }

        private void PresetButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && btn.Tag is string tagStr)
            {
                var parts = tagStr.Split(',');
                if (parts.Length == 2 && int.TryParse(parts[0], out int rows) && int.TryParse(parts[1], out int cols))
                {
                    FitGrid(rows, cols);
                }
            }
        }

        private void FitGrid(int rows, int cols)
        {
            double usableWidthMm = _pageWidthMm - (_marginLeftMm + _marginRightMm);
            double usableHeightMm = _pageHeightMm - (_marginTopMm + _marginBottomMm);

            double cellWidthMm = (usableWidthMm - ((cols - 1) * _gapMm)) / cols;
            double cellHeightMm = (usableHeightMm - ((rows - 1) * _gapMm)) / rows;

            if (cellWidthMm <= 0 || cellHeightMm <= 0) return;

            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
            {
                _imageWidthMm = Math.Min(cellWidthMm, cellHeightMm * _aspectRatio);
                _imageHeightMm = _imageWidthMm / _aspectRatio;
            }
            else
            {
                _imageWidthMm = cellWidthMm;
                _imageHeightMm = cellHeightMm;
            }

            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        // =========================================================================
        // 5. PAGE MARGINS (PRESETS & MANUAL CONTROLS)
        // =========================================================================
        private void CmbMarginPresets_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (!IsInitialized || _isUpdatingUi) return;

            switch (CmbMarginPresets.SelectedIndex)
            {
                case 0: // Normal / Standard (10.0 mm)
                    SetAllPageMargins(10.0);
                    break;
                case 1: // Narrow (5.0 mm)
                    SetAllPageMargins(5.0);
                    break;
                case 2: // None / Borderless (0.0 mm)
                    SetAllPageMargins(0.0);
                    break;
                case 3: // Wide (20.0 mm)
                    SetAllPageMargins(20.0);
                    break;
                case 4: // Custom (Manual)
                    // Keep current margins
                    break;
            }
        }

        private void SetAllPageMargins(double marginMm)
        {
            _marginTopMm = marginMm;
            _marginBottomMm = marginMm;
            _marginLeftMm = marginMm;
            _marginRightMm = marginMm;

            _isUpdatingUi = true;
            if (TxtPageMarginMm != null) TxtPageMarginMm.Text = $"{marginMm:F1} mm";
            if (TxtMarginTop != null) TxtMarginTop.Text = marginMm.ToString("0.#");
            if (TxtMarginBottom != null) TxtMarginBottom.Text = marginMm.ToString("0.#");
            if (TxtMarginLeft != null) TxtMarginLeft.Text = marginMm.ToString("0.#");
            if (TxtMarginRight != null) TxtMarginRight.Text = marginMm.ToString("0.#");
            _isUpdatingUi = false;

            RefreshWorkspace();
        }

        private void TxtPageMarginMm_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (!IsInitialized || _isUpdatingUi || TxtMarginTop == null || CmbMarginPresets == null) return;
            double m = ParseLengthMm(TxtPageMarginMm.Text, _marginLeftMm);
            _marginTopMm = m;
            _marginBottomMm = m;
            _marginLeftMm = m;
            _marginRightMm = m;

            _isUpdatingUi = true;
            if (TxtMarginTop != null) TxtMarginTop.Text = m.ToString("0.#");
            if (TxtMarginBottom != null) TxtMarginBottom.Text = m.ToString("0.#");
            if (TxtMarginLeft != null) TxtMarginLeft.Text = m.ToString("0.#");
            if (TxtMarginRight != null) TxtMarginRight.Text = m.ToString("0.#");
            if (CmbMarginPresets != null) CmbMarginPresets.SelectedIndex = 4; // Custom
            _isUpdatingUi = false;

            RefreshWorkspace();
        }

        private void BtnPageMarginUp_Click(object sender, RoutedEventArgs e)
        {
            SetAllPageMargins(_marginLeftMm + 1.0);
        }

        private void BtnPageMarginDown_Click(object sender, RoutedEventArgs e)
        {
            SetAllPageMargins(Math.Max(0.0, _marginLeftMm - 1.0));
        }

        private void IndependentMargin_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (!IsInitialized || _isUpdatingUi || TxtMarginTop == null || CmbMarginPresets == null) return;

            _marginTopMm = ParseLengthMm(TxtMarginTop.Text, _marginTopMm);
            _marginBottomMm = ParseLengthMm(TxtMarginBottom.Text, _marginBottomMm);
            _marginLeftMm = ParseLengthMm(TxtMarginLeft.Text, _marginLeftMm);
            _marginRightMm = ParseLengthMm(TxtMarginRight.Text, _marginRightMm);

            _isUpdatingUi = true;
            if (CmbMarginPresets != null) CmbMarginPresets.SelectedIndex = 4; // Custom
            _isUpdatingUi = false;

            RefreshWorkspace();
        }

        private void MarginGuide_Changed(object sender, RoutedEventArgs e)
        {
            if (!IsInitialized) return;
            RefreshWorkspace();
        }

        private void MenuMarginNormal_Click(object sender, RoutedEventArgs e) => SetAllPageMargins(10.0);
        private void MenuMarginNarrow_Click(object sender, RoutedEventArgs e) => SetAllPageMargins(5.0);
        private void MenuMarginNone_Click(object sender, RoutedEventArgs e) => SetAllPageMargins(0.0);
        private void MenuMarginWide_Click(object sender, RoutedEventArgs e) => SetAllPageMargins(20.0);

        // =========================================================================
        // 6. DIMENSION TEXTBOXES & CONTROLS
        // =========================================================================
        private void UpdateDimensionTextBoxes()
        {
            _isUpdatingUi = true;
            TxtWidthCm.Text = $"{(_imageWidthMm / 10.0):F1} cm";
            TxtHeightCm.Text = $"{(_imageHeightMm / 10.0):F1} cm";
            TxtGapMm.Text = $"{_gapMm:F1} mm";
            TxtPageMarginMm.Text = $"{_marginLeftMm:F1} mm";
            TxtMarginTop.Text = _marginTopMm.ToString("0.#");
            TxtMarginBottom.Text = _marginBottomMm.ToString("0.#");
            TxtMarginLeft.Text = _marginLeftMm.ToString("0.#");
            TxtMarginRight.Text = _marginRightMm.ToString("0.#");
            _isUpdatingUi = false;
        }

        private double ParseLengthCm(string text, double defaultMm)
        {
            string clean = text.Replace("cm", "", StringComparison.OrdinalIgnoreCase).Trim();
            if (double.TryParse(clean, NumberStyles.Any, CultureInfo.InvariantCulture, out double cmVal) ||
                double.TryParse(clean, out cmVal))
            {
                return Math.Max(0.5, cmVal) * 10.0;
            }
            return defaultMm;
        }

        private double ParseLengthMm(string text, double defaultMm)
        {
            string clean = text.Replace("mm", "", StringComparison.OrdinalIgnoreCase).Trim();
            if (double.TryParse(clean, NumberStyles.Any, CultureInfo.InvariantCulture, out double mmVal) ||
                double.TryParse(clean, out mmVal))
            {
                return Math.Max(0.0, mmVal);
            }
            return defaultMm;
        }

        private void TxtWidthCm_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (_isUpdatingUi || _sourceBitmap == null) return;
            _imageWidthMm = ParseLengthCm(TxtWidthCm.Text, _imageWidthMm);
            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
            {
                _imageHeightMm = _imageWidthMm / _aspectRatio;
                _isUpdatingUi = true;
                TxtHeightCm.Text = $"{(_imageHeightMm / 10.0):F1} cm";
                _isUpdatingUi = false;
            }
            RefreshWorkspace();
        }

        private void TxtHeightCm_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (_isUpdatingUi || _sourceBitmap == null) return;
            _imageHeightMm = ParseLengthCm(TxtHeightCm.Text, _imageHeightMm);
            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
            {
                _imageWidthMm = _imageHeightMm * _aspectRatio;
                _isUpdatingUi = true;
                TxtWidthCm.Text = $"{(_imageWidthMm / 10.0):F1} cm";
                _isUpdatingUi = false;
            }
            RefreshWorkspace();
        }

        private void TxtGapMm_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (_isUpdatingUi || _sourceBitmap == null) return;
            _gapMm = ParseLengthMm(TxtGapMm.Text, _gapMm);
            RefreshWorkspace();
        }

        private void BtnWidthUp_Click(object sender, RoutedEventArgs e)
        {
            _imageWidthMm += 5.0; // +0.5 cm
            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
                _imageHeightMm = _imageWidthMm / _aspectRatio;
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void BtnWidthDown_Click(object sender, RoutedEventArgs e)
        {
            _imageWidthMm = Math.Max(10.0, _imageWidthMm - 5.0); // -0.5 cm
            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
                _imageHeightMm = _imageWidthMm / _aspectRatio;
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void BtnHeightUp_Click(object sender, RoutedEventArgs e)
        {
            _imageHeightMm += 5.0;
            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
                _imageWidthMm = _imageHeightMm * _aspectRatio;
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void BtnHeightDown_Click(object sender, RoutedEventArgs e)
        {
            _imageHeightMm = Math.Max(10.0, _imageHeightMm - 5.0);
            if (ChkLockRatio.IsChecked == true && _aspectRatio > 0)
                _imageWidthMm = _imageHeightMm * _aspectRatio;
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void BtnGapUp_Click(object sender, RoutedEventArgs e)
        {
            _gapMm += 0.5;
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void BtnGapDown_Click(object sender, RoutedEventArgs e)
        {
            _gapMm = Math.Max(0.0, _gapMm - 0.5);
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void ChkAutoFitDuplicates_Changed(object sender, RoutedEventArgs e)
        {
            if (!IsInitialized) return;
            RefreshWorkspace();
        }

        private void BtnAutoFitGrid_Click(object sender, RoutedEventArgs e)
        {
            FitGrid(6, 4);
        }

        private void BtnResetDimensions_Click(object sender, RoutedEventArgs e)
        {
            _imageWidthMm = 50.0;
            _imageHeightMm = 50.0;
            _gapMm = 3.0;
            SetAllPageMargins(10.0);
            UpdateDimensionTextBoxes();
            RefreshWorkspace();
        }

        private void Options_Changed(object sender, RoutedEventArgs e)
        {
            if (!IsInitialized || _isUpdatingUi) return;
            RefreshWorkspace();
        }

        private void PosterDimension_TextChanged(object sender, RoutedEventArgs e)
        {
            if (!IsInitialized || _isUpdatingUi) return;
            RefreshWorkspace();
        }

        // =========================================================================
        // 7. WORKSPACE DRAWING & RENDERER
        // =========================================================================
        private void RefreshWorkspace()
        {
            A4Canvas.Children.Clear();
            if (_sourceBitmap == null) return;

            // Render Printable Margin Guide Line
            if (ChkShowMarginGuide.IsChecked == true)
            {
                MarginGuideCanvas.Visibility = Visibility.Visible;
                double guideX = _marginLeftMm * MmToDipFactor;
                double guideY = _marginTopMm * MmToDipFactor;
                double guideW = (_pageWidthMm - (_marginLeftMm + _marginRightMm)) * MmToDipFactor;
                double guideH = (_pageHeightMm - (_marginTopMm + _marginBottomMm)) * MmToDipFactor;

                Canvas.SetLeft(RectMarginGuide, guideX);
                Canvas.SetTop(RectMarginGuide, guideY);
                RectMarginGuide.Width = Math.Max(0, guideW);
                RectMarginGuide.Height = Math.Max(0, guideH);
            }
            else
            {
                MarginGuideCanvas.Visibility = Visibility.Collapsed;
            }

            if (!_isPosterMode)
            {
                RenderDuplicatorCanvas();
            }
            else
            {
                RenderPosterCanvas();
            }
        }

        private void RenderDuplicatorCanvas()
        {
            double gapMm = _gapMm;
            double usableWidthMm = _pageWidthMm - (_marginLeftMm + _marginRightMm);
            double usableHeightMm = _pageHeightMm - (_marginTopMm + _marginBottomMm);

            if (_imageWidthMm <= 0 || _imageHeightMm <= 0 || usableWidthMm <= 0 || usableHeightMm <= 0) return;

            double renderWidthMm = _imageWidthMm;
            double renderHeightMm = _imageHeightMm;
            bool shouldRotate = false;

            // Auto-rotate 90° check
            if (ChkAutoRotate.IsChecked == true)
            {
                int normalCols = (int)Math.Floor((usableWidthMm + gapMm) / (renderWidthMm + gapMm));
                int normalRows = (int)Math.Floor((usableHeightMm + gapMm) / (renderHeightMm + gapMm));
                int normalYield = Math.Max(0, normalCols) * Math.Max(0, normalRows);

                int rotatedCols = (int)Math.Floor((usableWidthMm + gapMm) / (renderHeightMm + gapMm));
                int rotatedRows = (int)Math.Floor((usableHeightMm + gapMm) / (renderWidthMm + gapMm));
                int rotatedYield = Math.Max(0, rotatedCols) * Math.Max(0, rotatedRows);

                if (rotatedYield > normalYield)
                {
                    shouldRotate = true;
                    renderWidthMm = _imageHeightMm;
                    renderHeightMm = _imageWidthMm;
                }
            }

            int cols = (int)Math.Floor((usableWidthMm + gapMm) / (renderWidthMm + gapMm));
            int rows = (int)Math.Floor((usableHeightMm + gapMm) / (renderHeightMm + gapMm));

            cols = Math.Max(1, cols);
            rows = Math.Max(1, rows);
            int capacity = cols * rows;

            // Copy limit
            bool limitEnabled = ChkLimitCopies.IsChecked == true && int.TryParse(TxtMaxCopies.Text, out int lim) && lim > 0;
            int totalDrawn = limitEnabled ? Math.Min(capacity, int.Parse(TxtMaxCopies.Text)) : capacity;

            // Batch multi-sheet calculation
            int totalBatchNeeded = int.TryParse(TxtTotalBatchCopies.Text, out int bCount) ? Math.Max(0, bCount) : 0;
            if (totalBatchNeeded > 0)
            {
                int totalSheets = (int)Math.Ceiling((double)totalBatchNeeded / capacity);
                TxtGridSummary.Text = $"Grid calculation: {totalDrawn} per sheet ({cols} x {rows} pattern) • Total Batch: {totalBatchNeeded} copies across {totalSheets} sheets";
                TxtCanvasSheetTitle.Text = $"Canvas: A4 Sheet 1 of {totalSheets}";
                if (TxtBatchSheetBadge != null)
                    TxtBatchSheetBadge.Text = $"{totalSheets} Sheet{(totalSheets > 1 ? "s" : "")}";
                if (TxtBatchCopiesDetail != null)
                {
                    int lastPageCopies = totalBatchNeeded % capacity == 0 ? capacity : totalBatchNeeded % capacity;
                    TxtBatchCopiesDetail.Text = $"{totalBatchNeeded} total copies: {totalSheets} A4 page(s) in PDF ({capacity}/page, last page has {lastPageCopies}).";
                }
            }
            else
            {
                TxtGridSummary.Text = $"Grid calculation: {totalDrawn} images fit this page ({cols} x {rows} pattern)";
                TxtCanvasSheetTitle.Text = "Canvas: A4 Sheet 1 of 1";
                if (TxtBatchSheetBadge != null)
                    TxtBatchSheetBadge.Text = "1 Sheet (Auto)";
                if (TxtBatchCopiesDetail != null)
                    TxtBatchCopiesDetail.Text = "Set total copies (e.g. 50, 100) to export a multi-page PDF spanning all sheets.";
            }

            double totalBlockWidthMm = (cols * renderWidthMm) + ((cols - 1) * gapMm);
            double totalBlockHeightMm = (rows * renderHeightMm) + ((rows - 1) * gapMm);

            // Alignment: Center vs Top-Left within margins
            bool isCentered = CmbAlignment.SelectedIndex == 0;
            double startX_Dip = isCentered
                ? (_marginLeftMm + ((usableWidthMm - totalBlockWidthMm) / 2.0)) * MmToDipFactor
                : _marginLeftMm * MmToDipFactor;

            double startY_Dip = isCentered
                ? (_marginTopMm + ((usableHeightMm - totalBlockHeightMm) / 2.0)) * MmToDipFactor
                : _marginTopMm * MmToDipFactor;

            double imgWidthDip = renderWidthMm * MmToDipFactor;
            double imgHeightDip = renderHeightMm * MmToDipFactor;
            double gapDip = gapMm * MmToDipFactor;

            // Draw dashed grid lines separating all columns & rows
            for (int c = 1; c < cols; c++)
            {
                double lineX = startX_Dip + c * (imgWidthDip + gapDip) - (gapDip / 2.0);
                var vLine = new Line
                {
                    X1 = lineX,
                    Y1 = startY_Dip,
                    X2 = lineX,
                    Y2 = startY_Dip + totalBlockHeightMm * MmToDipFactor,
                    Stroke = new SolidColorBrush(System.Windows.Media.Color.FromRgb(226, 232, 240)),
                    StrokeThickness = 1,
                    StrokeDashArray = new DoubleCollection { 3, 3 }
                };
                A4Canvas.Children.Add(vLine);
            }

            for (int r = 1; r < rows; r++)
            {
                double lineY = startY_Dip + r * (imgHeightDip + gapDip) - (gapDip / 2.0);
                var hLine = new Line
                {
                    X1 = startX_Dip,
                    Y1 = lineY,
                    X2 = startX_Dip + totalBlockWidthMm * MmToDipFactor,
                    Y2 = lineY,
                    Stroke = new SolidColorBrush(System.Windows.Media.Color.FromRgb(226, 232, 240)),
                    StrokeThickness = 1,
                    StrokeDashArray = new DoubleCollection { 3, 3 }
                };
                A4Canvas.Children.Add(hLine);
            }

            bool showCutMarks = ChkCutMarks.IsChecked == true;
            bool showBorder = ChkImageBorder.IsChecked == true;
            double borderMm = double.TryParse(TxtBorderThicknessMm.Text, out double bm) ? Math.Max(0.2, bm) : 0.5;
            double borderDip = borderMm * MmToDipFactor;
            Brush borderBrush = GetSelectedBorderBrush();

            int drawn = 0;
            for (int r = 0; r < rows; r++)
            {
                for (int c = 0; c < cols; c++)
                {
                    if (drawn >= totalDrawn) break;

                    double x = startX_Dip + c * (imgWidthDip + gapDip);
                    double y = startY_Dip + r * (imgHeightDip + gapDip);

                    var img = new Image
                    {
                        Source = _sourceBitmap,
                        Width = imgWidthDip,
                        Height = imgHeightDip,
                        Stretch = Stretch.Uniform
                    };

                    if (shouldRotate)
                    {
                        img.LayoutTransform = new RotateTransform(90);
                    }

                    Canvas.SetLeft(img, x);
                    Canvas.SetTop(img, y);
                    A4Canvas.Children.Add(img);

                    if (showBorder)
                    {
                        var bRect = new Rectangle
                        {
                            Width = imgWidthDip,
                            Height = imgHeightDip,
                            Stroke = borderBrush,
                            StrokeThickness = borderDip,
                            IsHitTestVisible = false
                        };
                        Canvas.SetLeft(bRect, x);
                        Canvas.SetTop(bRect, y);
                        A4Canvas.Children.Add(bRect);
                    }

                    if (showCutMarks)
                    {
                        DrawCutMarks(x, y, imgWidthDip, imgHeightDip);
                    }

                    drawn++;
                }
                if (drawn >= totalDrawn) break;
            }

            // Position Selection Adorner Box on the Top-Left Image
            SelectionAdornerCanvas.Visibility = Visibility.Visible;
            RectSelection.Width = imgWidthDip;
            RectSelection.Height = imgHeightDip;
            Canvas.SetLeft(RectSelection, startX_Dip);
            Canvas.SetTop(RectSelection, startY_Dip);

            // Badges
            TxtBadgeTop.Text = $"{(_imageWidthMm / 10.0):F1} cm";
            Canvas.SetLeft(BadgeTop, startX_Dip + (imgWidthDip / 2.0) - 18);
            Canvas.SetTop(BadgeTop, startY_Dip - 18);

            TxtBadgeLeft.Text = $"{(_imageHeightMm / 10.0):F1} cm";
            Canvas.SetLeft(BadgeLeft, startX_Dip - 38);
            Canvas.SetTop(BadgeLeft, startY_Dip + (imgHeightDip / 2.0) - 9);

            // Handles
            Canvas.SetLeft(HandleTL, startX_Dip - 3.5);
            Canvas.SetTop(HandleTL, startY_Dip - 3.5);

            Canvas.SetLeft(HandleTR, startX_Dip + imgWidthDip - 3.5);
            Canvas.SetTop(HandleTR, startY_Dip - 3.5);

            Canvas.SetLeft(HandleBL, startX_Dip - 3.5);
            Canvas.SetTop(HandleBL, startY_Dip + imgHeightDip - 3.5);

            Canvas.SetLeft(HandleBR, startX_Dip + imgWidthDip - 3.5);
            Canvas.SetTop(HandleBR, startY_Dip + imgHeightDip - 3.5);
        }

        private void DrawCutMarks(double x, double y, double w, double h)
        {
            double tick = 3.5 * MmToDipFactor;
            Brush tickBrush = Brushes.SlateGray;
            double thick = 0.75;

            var dashed = new Rectangle
            {
                Width = w,
                Height = h,
                Stroke = new SolidColorBrush(System.Windows.Media.Color.FromRgb(203, 213, 225)),
                StrokeThickness = 0.5,
                StrokeDashArray = new DoubleCollection { 2, 2 },
                IsHitTestVisible = false
            };
            Canvas.SetLeft(dashed, x);
            Canvas.SetTop(dashed, y);
            A4Canvas.Children.Add(dashed);

            AddTickLine(x - tick, y, x, y, tickBrush, thick);
            AddTickLine(x, y - tick, x, y, tickBrush, thick);

            AddTickLine(x + w, y, x + w + tick, y, tickBrush, thick);
            AddTickLine(x + w, y - tick, x + w, y, tickBrush, thick);

            AddTickLine(x - tick, y + h, x, y + h, tickBrush, thick);
            AddTickLine(x, y + h, x, y + h + tick, tickBrush, thick);

            AddTickLine(x + w, y + h, x + w + tick, y + h, tickBrush, thick);
            AddTickLine(x + w, y + h, x + w, y + h + tick, tickBrush, thick);
        }

        private void AddTickLine(double x1, double y1, double x2, double y2, Brush b, double t)
        {
            var l = new Line { X1 = x1, Y1 = y1, X2 = x2, Y2 = y2, Stroke = b, StrokeThickness = t, IsHitTestVisible = false };
            A4Canvas.Children.Add(l);
        }

        private Brush GetSelectedBorderBrush()
        {
            return CmbBorderColor.SelectedIndex switch
            {
                1 => Brushes.Gray,
                2 => Brushes.White,
                3 => Brushes.Red,
                _ => Brushes.Black,
            };
        }

        private XColor GetSelectedBorderXColor()
        {
            return CmbBorderColor.SelectedIndex switch
            {
                1 => XColors.Gray,
                2 => XColors.White,
                3 => XColors.Red,
                _ => XColors.Black,
            };
        }

        private void RenderPosterCanvas()
        {
            SelectionAdornerCanvas.Visibility = Visibility.Collapsed;

            int cols = int.TryParse(TxtPosterCols.Text, out int cVal) ? Math.Max(1, cVal) : 2;
            int rows = int.TryParse(TxtPosterRows.Text, out int rVal) ? Math.Max(1, rVal) : 2;

            string cleanOv = TxtPosterOverlapMm.Text.Replace("mm", "").Trim();
            double overlapMm = double.TryParse(cleanOv, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double ov) ? Math.Max(0, ov) : 10;
            double totalW = cols * (_pageWidthMm - overlapMm) + overlapMm;
            double totalH = rows * (_pageHeightMm - overlapMm) + overlapMm;

            string summaryMsg = $"Poster calculation: {cols * rows} A4 pages ({cols} across × {rows} down) • Overlap: {overlapMm:F0} mm\nTotal size: ~{totalW / 10:F1} × {totalH / 10:F1} cm";
            if (TxtPosterSummary != null)
                TxtPosterSummary.Text = summaryMsg;
            if (TxtGridSummary != null)
                TxtGridSummary.Text = summaryMsg;

            TxtCanvasSheetTitle.Text = $"Canvas: Poster Overview ({cols * rows} A4 Sheets)";

            var posterImg = new Image
            {
                Source = _sourceBitmap,
                Width = PaperBorder.Width,
                Height = PaperBorder.Height,
                Stretch = Stretch.Fill
            };
            A4Canvas.Children.Add(posterImg);

            double colStep = PaperBorder.Width / cols;
            double rowStep = PaperBorder.Height / rows;

            for (int i = 1; i < cols; i++)
            {
                var vLine = new Line
                {
                    X1 = i * colStep,
                    Y1 = 0,
                    X2 = i * colStep,
                    Y2 = PaperBorder.Height,
                    Stroke = Brushes.Crimson,
                    StrokeThickness = 1.5,
                    StrokeDashArray = new DoubleCollection { 4, 3 }
                };
                A4Canvas.Children.Add(vLine);
            }

            for (int j = 1; j < rows; j++)
            {
                var hLine = new Line
                {
                    X1 = 0,
                    Y1 = j * rowStep,
                    X2 = PaperBorder.Width,
                    Y2 = j * rowStep,
                    Stroke = Brushes.Crimson,
                    StrokeThickness = 1.5,
                    StrokeDashArray = new DoubleCollection { 4, 3 }
                };
                A4Canvas.Children.Add(hLine);
            }
        }

        // =========================================================================
        // 8. EXPORT TO PDF (MULTI-PAGE BATCH & POSTER TILES)
        // =========================================================================
        private void BtnExportPdf_Click(object sender, RoutedEventArgs e)
        {
            if (_sourceBitmap == null)
            {
                MessageBox.Show("Please load an image first.", "Notice", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            int totalBatchNeeded = int.TryParse(TxtTotalBatchCopies.Text, out int bCount) ? Math.Max(0, bCount) : 0;
            string defaultFileName = _isPosterMode
                ? "Poster_A4_Tiles.pdf"
                : (totalBatchNeeded > 0 ? $"Batch_{totalBatchNeeded}_Copies.pdf" : "Duplicated_A4_Output.pdf");

            var saveDlg = new SaveFileDialog
            {
                Filter = "PDF Document (*.pdf)|*.pdf",
                FileName = defaultFileName
            };

            if (saveDlg.ShowDialog() != true) return;

            try
            {
                TxtStatus.Text = "Generating PDF document...";
                var pdf = new PdfDocument();
                pdf.Info.Title = "PrintMaster A4 Output";

                if (!_isPosterMode)
                {
                    ExportDuplicatorPdf(pdf);
                }
                else
                {
                    ExportPosterPdf(pdf);
                }

                pdf.Save(saveDlg.FileName);
                TxtStatus.Text = "PDF exported successfully!";
                MessageBox.Show($"PDF successfully saved ({pdf.PageCount} page(s)) to:\n{saveDlg.FileName}", "Export Completed", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Export failed: {ex.Message}", "Export Error", MessageBoxButton.OK, MessageBoxImage.Error);
                TxtStatus.Text = "Export encountered an error.";
            }
        }

        private void ExportDuplicatorPdf(PdfDocument pdf)
        {
            var ms = new MemoryStream();
            var enc = new PngBitmapEncoder();
            enc.Frames.Add(BitmapFrame.Create(_sourceBitmap));
            enc.Save(ms);
            ms.Position = 0;

            using (var xImage = XImage.FromStream(() => new MemoryStream(ms.ToArray())))
            {
                const double mmToPt = 72.0 / 25.4;
                double gapMm = _gapMm;
                double usableWidthMm = _pageWidthMm - (_marginLeftMm + _marginRightMm);
                double usableHeightMm = _pageHeightMm - (_marginTopMm + _marginBottomMm);

                double renderWidthMm = _imageWidthMm;
                double renderHeightMm = _imageHeightMm;
                bool shouldRotate = false;

                if (ChkAutoRotate.IsChecked == true)
                {
                    int normalCols = (int)Math.Floor((usableWidthMm + gapMm) / (renderWidthMm + gapMm));
                    int normalRows = (int)Math.Floor((usableHeightMm + gapMm) / (renderHeightMm + gapMm));
                    int normalYield = Math.Max(0, normalCols) * Math.Max(0, normalRows);

                    int rotatedCols = (int)Math.Floor((usableWidthMm + gapMm) / (renderHeightMm + gapMm));
                    int rotatedRows = (int)Math.Floor((usableHeightMm + gapMm) / (renderWidthMm + gapMm));
                    int rotatedYield = Math.Max(0, rotatedCols) * Math.Max(0, rotatedRows);

                    if (rotatedYield > normalYield)
                    {
                        shouldRotate = true;
                        renderWidthMm = _imageHeightMm;
                        renderHeightMm = _imageWidthMm;
                    }
                }

                int cols = (int)Math.Floor((usableWidthMm + gapMm) / (renderWidthMm + gapMm));
                int rows = (int)Math.Floor((usableHeightMm + gapMm) / (renderHeightMm + gapMm));
                cols = Math.Max(1, cols);
                rows = Math.Max(1, rows);

                int capacityPerPage = cols * rows;

                int totalBatchNeeded = int.TryParse(TxtTotalBatchCopies.Text, out int bCount) ? Math.Max(0, bCount) : 0;
                bool limitEnabled = ChkLimitCopies.IsChecked == true && int.TryParse(TxtMaxCopies.Text, out int lim) && lim > 0;

                int totalCopiesToPrint = totalBatchNeeded > 0 ? totalBatchNeeded : (limitEnabled ? Math.Min(capacityPerPage, int.Parse(TxtMaxCopies.Text)) : capacityPerPage);
                int totalPages = (int)Math.Ceiling((double)totalCopiesToPrint / capacityPerPage);

                bool isCentered = CmbAlignment.SelectedIndex == 0;
                double totalBlockWidthMm = (cols * renderWidthMm) + ((cols - 1) * gapMm);
                double totalBlockHeightMm = (rows * renderHeightMm) + ((rows - 1) * gapMm);

                double startX_Pt = isCentered
                    ? (_marginLeftMm + ((usableWidthMm - totalBlockWidthMm) / 2.0)) * mmToPt
                    : _marginLeftMm * mmToPt;

                double startY_Pt = isCentered
                    ? (_marginTopMm + ((usableHeightMm - totalBlockHeightMm) / 2.0)) * mmToPt
                    : _marginTopMm * mmToPt;

                double imgWidthPt = renderWidthMm * mmToPt;
                double imgHeightPt = renderHeightMm * mmToPt;
                double gapPt = gapMm * mmToPt;

                bool showCutMarks = ChkCutMarks.IsChecked == true;
                bool showBorder = ChkImageBorder.IsChecked == true;
                double borderMm = double.TryParse(TxtBorderThicknessMm.Text, out double bm) ? Math.Max(0.2, bm) : 0.5;
                double borderPt = borderMm * mmToPt;
                XColor borderXColor = GetSelectedBorderXColor();

                int copiesRemaining = totalCopiesToPrint;

                for (int pageIdx = 0; pageIdx < totalPages; pageIdx++)
                {
                    var page = pdf.AddPage();
                    page.Size = PdfSharpCore.PageSize.A4;
                    page.Orientation = _isPortrait ? PdfSharpCore.PageOrientation.Portrait : PdfSharpCore.PageOrientation.Landscape;

                    using (var gfx = XGraphics.FromPdfPage(page))
                    {
                        int copiesOnThisPage = Math.Min(copiesRemaining, capacityPerPage);
                        int pageCount = 0;

                        for (int r = 0; r < rows; r++)
                        {
                            for (int c = 0; c < cols; c++)
                            {
                                if (pageCount >= copiesOnThisPage) break;

                                double x = startX_Pt + c * (imgWidthPt + gapPt);
                                double y = startY_Pt + r * (imgHeightPt + gapPt);

                                if (shouldRotate)
                                {
                                    var state = gfx.Save();
                                    gfx.TranslateTransform(x + imgWidthPt / 2, y + imgHeightPt / 2);
                                    gfx.RotateTransform(90);
                                    gfx.DrawImage(xImage, -imgHeightPt / 2, -imgWidthPt / 2, imgHeightPt, imgWidthPt);
                                    gfx.Restore(state);
                                }
                                else
                                {
                                    gfx.DrawImage(xImage, x, y, imgWidthPt, imgHeightPt);
                                }

                                if (showBorder)
                                {
                                    var pen = new XPen(borderXColor, borderPt);
                                    gfx.DrawRectangle(pen, x, y, imgWidthPt, imgHeightPt);
                                }

                                if (showCutMarks)
                                {
                                    DrawPdfCutMarks(gfx, x, y, imgWidthPt, imgHeightPt, mmToPt);
                                }

                                pageCount++;
                            }
                            if (pageCount >= copiesOnThisPage) break;
                        }

                        copiesRemaining -= copiesOnThisPage;
                    }
                }
            }
        }

        private void DrawPdfCutMarks(XGraphics gfx, double x, double y, double w, double h, double mmToPt)
        {
            double tick = 3.5 * mmToPt;
            var pen = new XPen(XColors.SlateGray, 0.5);

            var dashedPen = new XPen(XColors.LightGray, 0.4) { DashStyle = XDashStyle.Dash };
            gfx.DrawRectangle(dashedPen, x, y, w, h);

            gfx.DrawLine(pen, x - tick, y, x, y);
            gfx.DrawLine(pen, x, y - tick, x, y);

            gfx.DrawLine(pen, x + w, y, x + w + tick, y);
            gfx.DrawLine(pen, x + w, y - tick, x + w, y);

            gfx.DrawLine(pen, x - tick, y + h, x, y + h);
            gfx.DrawLine(pen, x, y + h, x, y + h + tick);

            gfx.DrawLine(pen, x + w, y + h, x + w + tick, y + h);
            gfx.DrawLine(pen, x + w, y + h, x + w, y + h + tick);
        }

        private void ExportPosterPdf(PdfDocument pdf)
        {
            int cols = int.TryParse(TxtPosterCols.Text, out int parsedCols) ? Math.Max(1, parsedCols) : 2;
            int rows = int.TryParse(TxtPosterRows.Text, out int parsedRows) ? Math.Max(1, parsedRows) : 2;

            string cleanOv = TxtPosterOverlapMm.Text.Replace("mm", "").Trim();
            double overlapMm = double.TryParse(cleanOv, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double ov) ? Math.Max(0, ov) : 10;
            bool printGuides = ChkPosterGuides.IsChecked == true;

            int pixelW = _sourceBitmap!.PixelWidth;
            int pixelH = _sourceBitmap.PixelHeight;

            int segmentWidth = pixelW / cols;
            int segmentHeight = pixelH / rows;

            int overlapPxX = (int)((overlapMm / _pageWidthMm) * segmentWidth);
            int overlapPxY = (int)((overlapMm / _pageHeightMm) * segmentHeight);

            int pageNum = 1;
            for (int row = 0; row < rows; row++)
            {
                for (int col = 0; col < cols; col++)
                {
                    int xStart = col * segmentWidth;
                    int yStart = row * segmentHeight;

                    int segW = (col < cols - 1) ? Math.Min(pixelW - xStart, segmentWidth + overlapPxX) : segmentWidth;
                    int segH = (row < rows - 1) ? Math.Min(pixelH - yStart, segmentHeight + overlapPxY) : segmentHeight;

                    var sourceRect = new Int32Rect(xStart, yStart, segW, segH);
                    var cropped = new CroppedBitmap(_sourceBitmap, sourceRect);

                    byte[] pngBytes;
                    using (var ms = new MemoryStream())
                    {
                        var encoder = new PngBitmapEncoder();
                        encoder.Frames.Add(BitmapFrame.Create(cropped));
                        encoder.Save(ms);
                        pngBytes = ms.ToArray();
                    }

                    var page = pdf.AddPage();
                    page.Size = PdfSharpCore.PageSize.A4;
                    page.Orientation = _isPortrait ? PdfSharpCore.PageOrientation.Portrait : PdfSharpCore.PageOrientation.Landscape;

                    using (var gfx = XGraphics.FromPdfPage(page))
                    using (var xImage = XImage.FromStream(() => new MemoryStream(pngBytes)))
                    {
                        const double mmToPt = 72.0 / 25.4;
                        double marginPt = _marginLeftMm * mmToPt;
                        double printWidthPt = page.Width - (2 * marginPt);
                        double printHeightPt = page.Height - (2 * marginPt);

                        gfx.DrawImage(xImage, marginPt, marginPt, printWidthPt, printHeightPt);

                        if (printGuides)
                        {
                            var font = new XFont("Arial", 8, XFontStyle.Regular);
                            var guidePen = new XPen(XColors.Crimson, 0.75) { DashStyle = XDashStyle.Dash };

                            if (col < cols - 1 && overlapMm > 0)
                            {
                                double overlapPt = overlapMm * mmToPt;
                                double lineX = marginPt + printWidthPt - overlapPt;
                                gfx.DrawLine(guidePen, lineX, marginPt, lineX, marginPt + printHeightPt);
                                gfx.DrawString($"Glue Sheet #{pageNum + 1} Here", font, XBrushes.Crimson, lineX + 4, marginPt + 20);
                            }

                            if (row < rows - 1 && overlapMm > 0)
                            {
                                double overlapPt = overlapMm * mmToPt;
                                double lineY = marginPt + printHeightPt - overlapPt;
                                gfx.DrawLine(guidePen, marginPt, lineY, marginPt + printWidthPt, lineY);
                                gfx.DrawString($"Glue Row #{row + 2} Here", font, XBrushes.Crimson, marginPt + 20, lineY - 4);
                            }

                            gfx.DrawString($"Poster Sheet #{pageNum} (Row {row + 1}/{rows}, Col {col + 1}/{cols})",
                                font, XBrushes.DarkGray, marginPt, page.Height - (marginPt / 2));
                        }

                        pageNum++;
                    }
                }
            }
        }

        // =========================================================================
        // 9. EXPORT TO 300 DPI HIGH-RES IMAGE
        // =========================================================================
        private void BtnExportImage_Click(object sender, RoutedEventArgs e)
        {
            if (_sourceBitmap == null)
            {
                MessageBox.Show("Please load an image first.", "Notice", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            var saveDlg = new SaveFileDialog
            {
                Filter = "PNG High-Res Image (*.png)|*.png|JPEG High-Res Image (*.jpg)|*.jpg",
                FileName = _isPosterMode ? "Poster_300DPI.png" : "Duplicated_A4_300DPI.png"
            };

            if (saveDlg.ShowDialog() != true) return;

            try
            {
                TxtStatus.Text = "Rendering 300 DPI image...";

                int targetPixelW = (int)Math.Round((_pageWidthMm / 25.4) * 300);
                int targetPixelH = (int)Math.Round((_pageHeightMm / 25.4) * 300);
                double scaleFactor = 300.0 / 96.0;

                var rtb = new RenderTargetBitmap(targetPixelW, targetPixelH, 300, 300, PixelFormats.Pbgra32);
                var visual = new DrawingVisual();
                using (var dc = visual.RenderOpen())
                {
                    dc.PushTransform(new ScaleTransform(scaleFactor, scaleFactor));
                    dc.DrawRectangle(Brushes.White, null, new Rect(0, 0, PaperBorder.Width, PaperBorder.Height));
                    var brush = new VisualBrush(A4Canvas);
                    dc.DrawRectangle(brush, null, new Rect(0, 0, PaperBorder.Width, PaperBorder.Height));
                    dc.Pop();
                }

                rtb.Render(visual);

                using (var fs = new FileStream(saveDlg.FileName, FileMode.Create))
                {
                    string ext = System.IO.Path.GetExtension(saveDlg.FileName).ToLowerInvariant();
                    BitmapEncoder encoder = (ext == ".jpg" || ext == ".jpeg")
                        ? new JpegBitmapEncoder { QualityLevel = 98 }
                        : new PngBitmapEncoder();

                    encoder.Frames.Add(BitmapFrame.Create(rtb));
                    encoder.Save(fs);
                }

                TxtStatus.Text = "300 DPI image exported successfully!";
                MessageBox.Show($"High-res 300 DPI image saved successfully to:\n{saveDlg.FileName}", "Image Exported", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Image export failed: {ex.Message}", "Export Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        // =========================================================================
        // 10. PRINT TO WINDOWS PRINTER
        // =========================================================================
        private void BtnPrintToPdfPaper_Click(object sender, RoutedEventArgs e)
        {
            if (_sourceBitmap == null)
            {
                MessageBox.Show("Please load an image first.", "Notice", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            var dlg = new PrintDialog();
            if (dlg.ShowDialog() == true)
            {
                try
                {
                    TxtStatus.Text = "Sending document to printer...";
                    dlg.PrintVisual(A4Canvas, "PrintMaster A4 Print");
                    TxtStatus.Text = "Print completed.";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Print failed: {ex.Message}", "Print Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void BtnSaveProject_Click(object sender, RoutedEventArgs e)
        {
            BtnExportPdf_Click(sender, e);
        }

        private void MenuExit_Click(object sender, RoutedEventArgs e) => Close();

        private void MenuAbout_Click(object sender, RoutedEventArgs e)
        {
            var about = new AboutWindow { Owner = this };
            about.ShowDialog();
        }
    }
}

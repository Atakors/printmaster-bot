using System;
using System.Threading.Tasks;
using System.Windows;

namespace PrintMasterA4
{
    public partial class SplashScreenWindow : Window
    {
        public SplashScreenWindow()
        {
            InitializeComponent();
        }

        public async Task RunLoadingSequenceAsync()
        {
            string[] steps = new[]
            {
                "Initializing print engines...",
                "Loading presets and paper profiles...",
                "Configuring high-res renderer...",
                "Ready!"
            };

            for (int i = 0; i < steps.Length; i++)
            {
                TxtStatus.Text = steps[i];
                int targetVal = (i + 1) * 25;
                while (ProgBar.Value < targetVal)
                {
                    ProgBar.Value += 2;
                    await Task.Delay(18);
                }
                await Task.Delay(180);
            }
            await Task.Delay(250);
        }
    }
}

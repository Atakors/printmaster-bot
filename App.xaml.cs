using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;

namespace PrintMasterA4
{
    public partial class App : Application
    {
        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            AppDomain.CurrentDomain.UnhandledException += (s, args) =>
            {
                try { File.WriteAllText("crash.txt", args.ExceptionObject?.ToString()); } catch { }
            };

            DispatcherUnhandledException += (s, args) =>
            {
                try { File.WriteAllText("crash.txt", args.Exception?.ToString()); } catch { }
            };

            ShutdownMode = ShutdownMode.OnExplicitShutdown;

            var splash = new SplashScreenWindow();
            splash.Show();

            await splash.RunLoadingSequenceAsync();

            var mainWin = new MainWindow();
            MainWindow = mainWin;
            ShutdownMode = ShutdownMode.OnMainWindowClose;

            mainWin.Show();
            splash.Close();
        }
    }
}

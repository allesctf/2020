using System;
using Notes.Models;
using Notes.Models.Notes;
using Notes.Models.PasswordChecker;
using Notes.ViewModels;
using Notes.Views;
using Prism;
using Prism.Ioc;
using Prism.Mvvm;
using Prism.Navigation;
using Prism.Unity;
using Xamarin.Essentials;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace Notes
{
    public partial class App : PrismApplication
    {
        public NotesSqlLite NotesSqlLite;

        public App()
        {
        }

        public App(IPlatformInitializer initializer) : base(initializer)
        {

        }


        protected override void RegisterTypes(IContainerRegistry containerRegistry)
        {
            containerRegistry.RegisterForNavigation<NavigationPage>();
            containerRegistry.RegisterForNavigation<MainPage>();
            containerRegistry.RegisterForNavigation<NotesPage>();

            containerRegistry.RegisterInstance<IPasswordChecker>(new PasswordChecker());

            NotesSqlLite = new NotesSqlLite();
            containerRegistry.RegisterInstance<INotes>(NotesSqlLite);

            ViewModelLocationProvider.Register<MainPage, MainPageViewModel>();
            ViewModelLocationProvider.Register<NotesPage, NotesPageViewModel>();
        }

        protected override async void OnInitialized()
        {
            InitializeComponent();

            await NavigationService.NavigateAsync($"/{nameof(NavigationPage)}/{nameof(MainPage)}");
        }
    }
}

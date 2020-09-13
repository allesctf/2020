using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using AsyncAwaitBestPractices.MVVM;
using Notes.Models;
using Notes.Models.Notes;
using Notes.Models.PasswordChecker;
using Notes.Views;
using Prism.Mvvm;
using Prism.Navigation;
using Xamarin.Forms;

namespace Notes.ViewModels
{
    public class MainPageViewModel : BindableBase
    {
        private readonly IPasswordChecker _passwordChecker;
        private readonly INavigationService _navigationService;
        private readonly INotes _notes;

        public string Title => "My Secret Notes";

        private string _passwordEntry = "";
        public string PasswordEntry
        {
            get => _passwordEntry;
            set => SetProperty(ref _passwordEntry, value);
        }

        private string _error = "";
        public string Error
        {
            get => _error;
            set => SetProperty(ref _error, value);
        }

        private bool _loading = false;
        public bool Loading
        {
            get => _loading;
            set => SetProperty(ref _loading, value);
        }

        public ICommand SubmitCommand => new AsyncCommand(SubmitPassword);

        public MainPageViewModel(INavigationService navigationService, IPasswordChecker passwordChecker, INotes notes)
        {
            _navigationService = navigationService;
            _passwordChecker = passwordChecker;
            _notes = notes;
        }

        private async Task SubmitPassword()
        {
            if (_passwordChecker.CheckPassword(PasswordEntry))
            {
                Loading = true;
                bool result = await _notes.Init(PasswordEntry);

                if (result)
                {
                    await _navigationService.NavigateAsync(nameof(NotesPage));

                    Error = "Correct";
                }
                else
                {
                    Error = "Wrong Password entered";
                }

                Loading = false;
            }
            else
            {
                Error = "Wrong Password entered";
            }
        }
    }
}

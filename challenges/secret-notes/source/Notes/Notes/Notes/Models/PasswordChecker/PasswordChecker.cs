using System;
using Xamarin.Forms;

namespace Notes.Models.PasswordChecker
{
    public class PasswordChecker : IPasswordChecker
    {
        public bool CheckPassword(string password)
        {
            return password.Length == 29 && DependencyService.Get<IPasswordChecker>().CheckPassword(password);
        }
    }
}

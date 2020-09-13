using System;
using System.Text;
using Notes.Models.PasswordChecker;
using Xamarin.Forms;
using PasswordChecker = Notes.UWP.Models.PasswordChecker.PasswordChecker;

[assembly: Dependency(typeof(PasswordChecker))]
namespace Notes.UWP.Models.PasswordChecker
{
    public class PasswordChecker : IPasswordChecker
    {
        public bool CheckPassword(string password)
        {
            var bytes = Encoding.ASCII.GetBytes(password);
            var pass = Array.ConvertAll(bytes, item => (int)item);

            bool check = true;
            check &= pass[15] - pass[24] - pass[1] + pass[6] == 90;
            check &= pass[17] - pass[23] - pass[2] == -123;
            check &= pass[28] == 125;
            check &= pass[17] * pass[24] - pass[3] - pass[23] * pass[2] == -4937;
            check &= pass[11] * pass[14] - pass[26] + pass[7] + pass[16] == 5105;
            check &= pass[3] - pass[6] == -30;
            check &= pass[21] == 105;
            check &= pass[9] * pass[27] - pass[24] * pass[21] - pass[25] == 1129;
            check &= pass[18] * pass[6] + pass[23] * pass[3] + pass[20] == 17936;
            check &= pass[7] - pass[13] + pass[19] * pass[5] == 13413;
            check &= pass[10] * pass[0] * pass[12] - pass[26] == 837149;

            return check;
        }
    }
}
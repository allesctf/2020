namespace Notes.Models.PasswordChecker
{
    public interface IPasswordChecker
    {
        bool CheckPassword(string password);
    }
}

using System.IO;
using Notes.Droid.Models.Notes;
using Notes.Models.Notes;
using Xamarin.Forms;
using Application = Android.App.Application;
using Environment = System.Environment;

[assembly: Dependency(typeof(FileAccessHelper))]
namespace Notes.Droid.Models.Notes
{
	public class FileAccessHelper : IFileAccessHelper
    {
        public string GetLocalFilePath(string filename)
        {
            string path = Environment.GetFolderPath(Environment.SpecialFolder.Personal);
            string dbPath = Path.Combine(path, filename);

            CopyDatabaseIfNotExists(dbPath, filename);

            return dbPath;
        }

        private void CopyDatabaseIfNotExists(string dbPath, string filename)
        {
            if (!File.Exists(dbPath))
            {
                using (var br = new BinaryReader(Application.Context.Assets.Open(filename)))
                {
                    using (var bw = new BinaryWriter(new FileStream(dbPath, FileMode.Create)))
                    {
                        byte[] buffer = new byte[2048];
                        int length = 0;
                        while ((length = br.Read(buffer, 0, buffer.Length)) > 0)
                        {
                            bw.Write(buffer, 0, length);
                        }
                    }
                }
            }
        }
    }
}
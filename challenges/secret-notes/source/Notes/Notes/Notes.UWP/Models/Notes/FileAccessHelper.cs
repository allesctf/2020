using System.IO;
using System.IO.IsolatedStorage;
using System.Reflection;
using Notes.Models.Notes;
using Notes.UWP.Models.Notes;
using Xamarin.Forms;

[assembly: Dependency(typeof(FileAccessHelper))]
namespace Notes.UWP.Models.Notes
{
	public class FileAccessHelper : IFileAccessHelper
    {
        public string GetLocalFilePath(string filename)
        {
            string path = Windows.Storage.ApplicationData.Current.LocalFolder.Path;
            string dbPath = Path.Combine(path, filename);

            CopyDatabaseIfNotExists(dbPath, filename);

            return dbPath;
        }

        public void CopyDatabaseIfNotExists(string dbPath, string filename)
        {
            var storageFile = IsolatedStorageFile.GetUserStoreForApplication();

            if (!storageFile.FileExists(dbPath))
            {
                var assembly = this.GetType()
                    .GetTypeInfo()
                    .Assembly;
                
                
                using (var resourceStream = assembly.GetManifestResourceStream($"Notes.UWP.{filename}"))
                {
                    using (var fileStream = storageFile.CreateFile(dbPath))
                    {
                        byte[] readBuffer = new byte[4096];
                        int bytes = -1;

                        while ((bytes = resourceStream.Read(readBuffer, 0, readBuffer.Length)) > 0)
                        {
                            fileStream.Write(readBuffer, 0, bytes);
                        }
                    }
                }
            }
        }
    }
}

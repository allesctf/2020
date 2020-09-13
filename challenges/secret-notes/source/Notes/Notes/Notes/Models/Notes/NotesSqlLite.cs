using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using Notes.Models.PasswordChecker;
using Notes.ViewModels;
using SQLite;
using Xamarin.Forms;

namespace Notes.Models.Notes
{
    public class NotesSqlLite : INotes
    {
        private string _databasePath;
        private SQLiteAsyncConnection _db;

        public event EventHandler<Note> NoteRemoved;

        public NotesSqlLite()
        {
            _databasePath = DependencyService.Get<IFileAccessHelper>().GetLocalFilePath("SecretNotes.db");
        }


        public async Task<bool> Init(string password)
        {
            try
            {
                if (_db != null)
                {
                    await _db.CloseAsync().ConfigureAwait(false);
                }

                var options = new SQLiteConnectionString(_databasePath, true,
                    key: password);

                _db = new SQLiteAsyncConnection(options);

                await _db.CreateTableAsync<Note>();
            }
            catch (Exception)
            {
                return false;
            }
            

            return true;
        }

        public async Task<List<Note>> GetAllNotes()
        {
            return await _db.Table<Note>().ToListAsync().ConfigureAwait(false);
        }

        public async Task<Note> AddNewNote()
        {
            var note = new Note();
            await _db.InsertAsync(note).ConfigureAwait(false);

            return note;
        }

        public async Task ChangeNote(Note note)
        {
            await _db.UpdateAsync(note).ConfigureAwait(false);
        }

        public async Task RemoveNote(Note note)
        {
            await _db.DeleteAsync(note).ConfigureAwait(false);

            NoteRemoved?.Invoke(this, note);
        }
    }
}

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using AsyncAwaitBestPractices.MVVM;
using Notes.Models.Notes;
using Prism.Mvvm;
using SQLite;

namespace Notes.ViewModels
{
    [Table("Note")]
    public class Note : BindableBase
    {
        [PrimaryKey, AutoIncrement]
        public int Id { get; set; }
        public string Title { get; set; }
        public string Content { get; set; }

        private INotes _notes;

        public ICommand RemoveCommand => new AsyncCommand(Remove);
        public ICommand TextChangedCommand => new AsyncCommand(TextChanged);

        public Note()
        {
            _notes = ((App) App.Current).NotesSqlLite;
        }

        private async Task Remove()
        {
            await _notes.RemoveNote(this).ConfigureAwait(false);
        }

        private async Task TextChanged()
        {
            await _notes.ChangeNote(this).ConfigureAwait(false);
        }
    }
}

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using AsyncAwaitBestPractices;
using AsyncAwaitBestPractices.MVVM;
using Notes.Models.Notes;
using Prism.Mvvm;
using Xamarin.Forms;

namespace Notes.ViewModels
{
    public class NotesPageViewModel : BindableBase
    {
        private readonly INotes _notes;

        public string Title => "My Secret Notes";

        public ICommand NewNoteCommand => new AsyncCommand(NewNote);

        public ObservableCollection<Note> NotesBindings { get; set; } = new ObservableCollection<Note>();

        public NotesPageViewModel(INotes notes)
        {
            _notes = notes;

            _notes.NoteRemoved += NotesOnNoteRemoved;

            Init().SafeFireAndForget();
        }

        private async Task Init()
        {
            var notes = await _notes.GetAllNotes().ConfigureAwait(false);

            Device.BeginInvokeOnMainThread(() =>
            {
                foreach (var note in notes)
                {
                    NotesBindings.Add(note);
                }
            });
        }

        private void NotesOnNoteRemoved(object sender, Note note)
        {
            Device.BeginInvokeOnMainThread(() => NotesBindings.Remove(note));
        }

        private async Task NewNote()
        {
            Note note = await _notes.AddNewNote();
            NotesBindings.Add(note);
        }
    }
}

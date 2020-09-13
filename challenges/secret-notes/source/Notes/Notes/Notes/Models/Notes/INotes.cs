using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Notes.ViewModels;

namespace Notes.Models.Notes
{
    public interface INotes
    {
        event EventHandler<Note> NoteRemoved;

        Task<bool> Init(string password);
        Task<List<Note>> GetAllNotes();
        Task<Note> AddNewNote();
        Task ChangeNote(Note note);
        Task RemoveNote(Note note);
    }
}

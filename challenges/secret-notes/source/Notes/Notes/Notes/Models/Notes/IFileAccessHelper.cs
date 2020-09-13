using System;
using System.Collections.Generic;
using System.Text;

namespace Notes.Models.Notes
{
    public interface IFileAccessHelper
    {
        string GetLocalFilePath(string filename);
    }
}

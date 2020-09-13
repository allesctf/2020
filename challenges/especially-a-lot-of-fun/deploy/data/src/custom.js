function updateChecksum(val) {
    if (val == "JohnDoe")
    {
        document.getElementById("checksum").value = "3a9d0a";
    }
    if (val == "???")
    {
        document.getElementById("checksum").value = "FFFFFFFF";
    }
  }
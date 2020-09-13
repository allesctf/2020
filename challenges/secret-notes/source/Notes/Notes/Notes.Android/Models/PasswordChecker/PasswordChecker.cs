using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Android.App;
using Android.Content;
using Android.Graphics;
using Android.Hardware.Camera2;
using Android.Hardware.Camera2.Params;
using Android.OS;
using Java.Util;
using Notes.Models.PasswordChecker;
using Xamarin.Essentials;
using Xamarin.Forms;
using Camera = Android.Hardware.Camera;
using Exception = System.Exception;
using PasswordChecker = Notes.Droid.Models.PasswordChecker.PasswordChecker;

[assembly: Dependency(typeof(PasswordChecker))]
namespace Notes.Droid.Models.PasswordChecker
{
    public class PasswordChecker : IPasswordChecker
    {
        public bool CheckPassword(string password)
        {
            CameraManager camMan = (CameraManager)Forms.Context.GetSystemService(Context.CameraService);
            var camera0 = camMan.GetCameraIdList()[0];
            CameraCharacteristics characteristics = camMan.GetCameraCharacteristics(camera0);

            var map = (StreamConfigurationMap)characteristics.Get(CameraCharacteristics.ScalerStreamConfigurationMap);

            int largestPicSize = 0;
            var x = map.GetOutputSizes((int)ImageFormatType.Jpeg);
            foreach (Android.Util.Size s in x)
            {
                int picSize = s.Height * s.Width;

                if (picSize > largestPicSize)
                {
                    largestPicSize = picSize;
                }
            }
            var mp = (int) Math.Ceiling(largestPicSize / 1024000.0);


            var mainDisplayInfo = DeviceDisplay.MainDisplayInfo;
            var width = (int) mainDisplayInfo.Width;
            var height = (int) mainDisplayInfo.Height;

            var bytes = Encoding.ASCII.GetBytes(password);
            var pass = Array.ConvertAll(bytes, item => (int)item);

            bool check = true;
            check &= pass[22] - pass[4] - pass[26] + pass[10] == 8 * mp;
            check &= pass[20] + pass[27] + pass[6] == 249;
            check &= pass[21] - pass[25] + pass[27] - pass[8] == 61;
            check &= pass[24] + pass[9] * pass[21] + pass[23] == 12219;
            check &= pass[0] + pass[28] * pass[12] + pass[19] - pass[11] == 39 + 13 * width;
            check &= pass[10] * pass[22] + pass[19] + pass[0] - pass[28] == 13274;
            check &= pass[5] == 123;
            check &= pass[17] - pass[25] - pass[2] + pass[18] == 35;
            check &= pass[9] + pass[24] - pass[21] + pass[2] - pass[15] == 19;
            check &= pass[13] * pass[22] + pass[16] * pass[11] == 1878 + 9 * height;
            check &= pass[4] == 71 + mp;

            return check;
        }
    }
}
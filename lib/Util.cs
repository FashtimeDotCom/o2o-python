using System;

using System.Collections.Generic;
using System.Text;

namespace WinFormDemo
{
    class Util
    {


        /// <summary>
        /// 检测空或NULL
        /// </summary>
        /// <param name="value"></param>
        /// <returns></returns>
        public static bool checkEmptyorNull(String value)
        {
            return value == null || value.Trim().Equals("");
        }

        /// <summary>
        /// 返回两个时间差(秒数)
        /// </summary>
        /// <param name="DateTime1"></param>
        /// <param name="DateTime2"></param>
        /// <returns></returns>
        public static int DateDiff(DateTime DateTime1, DateTime DateTime2)
        {
            int dateDiff;
            TimeSpan ts1 = new TimeSpan(DateTime1.Ticks);
            TimeSpan ts2 = new TimeSpan(DateTime2.Ticks);
            TimeSpan ts = ts1.Subtract(ts2).Duration();

            dateDiff = (int)ts.TotalSeconds;
            return dateDiff;
        }

        /// <summary>
        /// 返回两个时间差(毫秒数)
        /// </summary>
        /// <param name="DateTime1"></param>
        /// <param name="DateTime2"></param>
        /// <returns></returns>
        public static double DateDiffMillSecond(DateTime DateTime1, DateTime DateTime2)
        {
            double dateDiff;
            TimeSpan ts1 = new TimeSpan(DateTime1.Ticks);
            TimeSpan ts2 = new TimeSpan(DateTime2.Ticks);
            TimeSpan ts = ts1.Subtract(ts2).Duration();

            dateDiff = ts.TotalMilliseconds;
            return dateDiff;
        }

        /*******************************************************************
      * * 函数名称：ToHexString
      * * 功    能：获取字节数组的16进制
      * * 参    数：bytes 字节数组
      * * 返 回 值：
      * 
      * *******************************************************************/
        public static string ToHexStrByByte(byte[] bytes)
        {
            if (bytes != null)
            {
                char[] chars = new char[bytes.Length * 2];
                for (int i = 0; i < bytes.Length; i++)
                {
                    int b = bytes[i];
                    chars[i * 2] = hexDigits[b >> 4];
                    chars[i * 2 + 1] = hexDigits[b & 0xF];
                }
                return new string(chars);
            }
            else
                return null;
        }

        static char[] hexDigits = {
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
        /*******************************************************************
       * * 函数名称：ToHexByte
       * * 功    能：获取16进制字符串的字节数组
       * * 参    数：hexString 16进制字符串
       * * 返 回 值：
       * 
       * *******************************************************************/
        public static byte[] ToByteByHexStr(string hexString)
        {
            if (hexString == null)
                return null;

            hexString = hexString.Replace(" ", "");
            if ((hexString.Length % 2) != 0)
                hexString += " ";
            byte[] returnBytes = new byte[hexString.Length / 2];
            for (int i = 0; i < returnBytes.Length; i++)
                returnBytes[i] = Convert.ToByte(hexString.Substring(i * 2, 2), 16);
            return returnBytes;
        }

        /// <summary>
        /// 将16进制的Byte数组转换为UShort数组
        /// </summary>
        /// <param name="source"></param>
        /// <returns></returns>
        public static ushort[] ToUShortFromByte(byte[] source)
        {
            int length = source.Length;

            ushort[] output = new ushort[length / 2];
            for (int i = 0; i < output.Length; ++i)
            {
                output[i] = (ushort)(source[i * 2 + 1] | source[i * 2] << 8);
            }
            return output;
        }

        /// <summary>
        /// 将16进制的字符串转换为UShort数组
        /// </summary>
        /// <param name="source"></param>
        /// <returns></returns>
        public static ushort[] ToUShortFromHexStr(String str)
        {
            byte[] source = ToByteByHexStr(str);
            int length = source.Length;

            ushort[] output = new ushort[length / 2];
            for (int i = 0; i < output.Length; ++i)
            {
                output[i] = (ushort)(source[i * 2 + 1] | source[i * 2] << 8);
            }
            return output;
        }

        /// <summary>
        /// 格式化EPC或User等
        /// </summary>
        /// <param name="str"></param>
        /// <returns></returns>
        public static String DisplayFormatHexStr(String str)
        {
            if (str != null)
            {
                for (int i = 4; i < str.Length; i = i + 5)
                {
                    str = str.Insert(i, "-");
                }
                return str;
            }
            else
                return "";
        }

        /// <summary>
        /// 替换字符'-'
        /// </summary>
        /// <param name="str"></param>
        /// <returns></returns>
        public static String FormatHexStr(String str)
        {
            if (str == null)
                return "";
            else
                return str.Replace("-", "");
        }

        /// <summary>
        /// 检查是否全部16进制
        /// </summary>
        /// <param name="s"></param>
        /// <returns></returns>
        public static bool isHex(string s)
        {
            int Flag = 0;
            char[] str = s.ToCharArray();
            for (int i = 0; i < str.Length; i++)
            {
                if (Char.IsNumber(str[i])
                || str[i] == (char)45//中划线
                || (str[i] >= (char)65 && str[i] <= (char)70)//A-F
                || (str[i] >= (char)97 && str[i] <= (char)102))//a-f
                {
                    Flag++;
                }
                else
                {
                    Flag = -1;
                    break;
                }
            }
            if (Flag > 0)
            {
                return true;
            }
            else
            {
                return false;
            }
        }

    }
}

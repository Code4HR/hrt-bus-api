using System;
using System.Net;
using System.Threading;
using System.Web;

namespace HRTBusAPI
{
    public class Global : HttpApplication
    {
        protected void Application_Start(object sender, EventArgs e)
        {
            new Thread(RefreshData).Start();
        }

        private static string _portNumber = "80";
        public static UInt64 RefreshCount;
        public static DateTime LastRefresh = DateTime.UtcNow.AddHours(-5);

        private static void RefreshData()
        {
            while(true)
            {
                try
                {
                    
                    var request = WebRequest.Create(string.Format("http://localhost:{0}/refresh", _portNumber));
                    request.GetResponse().Close();
                    RefreshCount++;
                    LastRefresh = DateTime.UtcNow.AddHours(-5);
                }
                catch (Exception ex)
                {
                    
                }

                Thread.Sleep(TimeSpan.FromSeconds(20));
            }
        }

        protected void Session_Start(object sender, EventArgs e)
        {

        }

        protected void Application_BeginRequest(object sender, EventArgs e)
        {
            _portNumber = Request.Url.Port.ToString();
        }

        protected void Application_AuthenticateRequest(object sender, EventArgs e)
        {

        }

        protected void Application_Error(object sender, EventArgs e)
        {

        }

        protected void Session_End(object sender, EventArgs e)
        {

        }

        protected void Application_End(object sender, EventArgs e)
        {

        }
    }
}
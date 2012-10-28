using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using HRTBusAPI.API;
using Nancy;

namespace HRTBusAPI
{
    public class BusDataModule : NancyModule
    {
        private static readonly List<BusCheckin> Checkins = new List<BusCheckin>();

        public BusDataModule()
        {
            Get["/refresh"] = RefreshBusData;

            Get["/api/raw"] = parameters => Checkins.Select(c => c.ToString()).Aggregate((s1, s2) => s1 + "<br>" + s2);

            Get["/api/route"] =
                parameters =>
                    {
                        var result = new List<RouteModel>();
                        foreach (var checkin in Checkins.Where(checkin => checkin.HasRoute))
                        {
                            // Add the route if it doesn't exist
                            if (!result.Exists(r => r.route == checkin.Route))
                                result.Add(new RouteModel { route = checkin.Route });

                            // Get the route from the list
                            var route = result.First(r => r.route == checkin.Route);

                            // Don't add the checkin if there is already a newer one for this bus
                            if (route.buses.Exists(b => b.id == checkin.BusId)) continue;

                            route.buses.Add(new BusCheckinModel(checkin));
                            route.buses.Sort((x, y) => x.id.CompareTo(y.id));
                        }
                        result.Sort((x, y) => x.route.CompareTo(y.route));
                        return Response.AsJson(result);
                    };

            Get["/api/route/{route}"] =
                parameters =>
                    {
                        var checkins = Checkins.FindAll(c => c.Route == parameters.route);
                        var result = new RouteModel { route = parameters.route };
                        foreach (var checkin in checkins.Where(checkin => !result.buses.Exists(b=>b.id == checkin.BusId)))
                        {
                            result.buses.Add(new BusCheckinModel(checkin));
                        }
                        result.buses.Sort((x, y) => x.id.CompareTo(y.id));
                        return Response.AsJson(result);
                    };

            Get["/api/bus/{id}"] =
                parameters =>
                {
                    var checkins = Checkins.FindAll(c => c.BusId == parameters.id);
                    var result = checkins.Select(checkin => new BusCheckinModel(checkin)).ToList();
                    return Response.AsJson(result);
                };
        }

        private object RefreshBusData(dynamic parameters)
        {
            try
            {
                var contents = GetFileFromServer(new Uri("ftp://216.54.15.3/Anrd/hrtrtf.txt"));
                var newCheckins = GetBusCheckinsFromFile(contents);   // oldest first

                var duplicates = 0;
                var withoutRoute = 0;
                var routeLookedup = 0;

                foreach (var checkin in newCheckins)
                {
                    if(Checkins.Exists(c=>c.CheckinTime == checkin.CheckinTime && c.BusId == checkin.BusId))
                    {
                        duplicates++;
                    }
                    else
                    {
                        if(!checkin.HasRoute)
                        {
                            withoutRoute++;
                            var oldCheckinWithRoute = Checkins.FirstOrDefault(c => c.HasRoute && c.BusId == checkin.BusId);
                            if(oldCheckinWithRoute != null)
                            {
                                routeLookedup++;
                                checkin.HasRoute = true;
                                checkin.RouteLookedUp = true;
                                checkin.Route = oldCheckinWithRoute.Route;
                                checkin.Direction = oldCheckinWithRoute.Direction;
                            }
                        }
                        Checkins.Insert(0, checkin); // newest first
                    }
                }

                var removed = Checkins.RemoveAll(c => c.CheckinTime < DateTime.UtcNow.AddHours(-5).AddHours(-1));
                var percentWithRoute = Checkins.FindAll(c => c.HasRoute).Count*100.0/Checkins.Count;

                return string.Format("{0} checkins in FTP file.<br>" +
                                     "{1} were duplicates.<br>" +
                                     "{2} new checkins didn't have a route. Routes were found for {3} of those.<br>" +
                                     "{4} were removed because they were more than an hour old.<br>" +
                                     "{5} checkins now in memory.<br>" +
                                     "{6}% have a route.",
                    newCheckins.Count,
                    duplicates,
                    withoutRoute,
                    routeLookedup,
                    removed,
                    Checkins.Count,
                    (int)percentWithRoute);
            }
            catch (Exception ex)
            {
                return ex.Message + "<br>" + ex.StackTrace;
            }
        }

        public static string GetFileFromServer(Uri serverUri)
        {
            var newFileData = new WebClient().DownloadData(serverUri.ToString());
            return System.Text.Encoding.UTF8.GetString(newFileData);
        }

        public static List<BusCheckin> GetBusCheckinsFromFile(string file)
        {
            if (String.IsNullOrEmpty(file))
                return null;

            return file.Split('\n', '\r')
                .Select(BusCheckin.Parse)
                .Where(checkin => checkin != null)
                .ToList();
        }
    }
}
using System;

namespace HRTBusAPI
{
    public class BusCheckin
    {
        public DateTime CheckinTime { get; set; }
        public int BusId { get; set; }
        public string Location { get; set; }
        public double Lat { get; set; }
        public double Lon { get; set; }
        public bool LocationValid { get; set; }
        public int Adherence { get; set; }
        public bool AdherenceValid { get; set; }
        public bool HasRoute { get; set; }
        public bool RouteLookedUp { get; set; }
        public int Route { get; set; }
        public int Direction { get; set; }
        public int StopId { get; set; }
        public string RawData { get; set; }

        public override string ToString()
        {
            return string.Format("{0} {1} {2} {3} {4} {5} {6}",
                                 CheckinTime.ToString(),
                                 BusId,
                                 Location,
                                 Adherence,
                                 Route,
                                 Direction,
                                 RouteLookedUp);
        }

        public static BusCheckin Parse(string data)
        {
            if (!String.IsNullOrEmpty(data))
            {
                var checkin = new BusCheckin();
                string[] parts = data.Split(',');
                DateTime checkinTime;
                int busId;

                if (DateTime.TryParse(parts[1] + "/" + DateTime.UtcNow.AddHours(-5).Year.ToString() + " " + parts[0], out checkinTime) &&
                    Int32.TryParse(parts[2], out busId))
                {
                    checkin.RawData = data;
                    checkin.RouteLookedUp = false;
                    checkin.CheckinTime = checkinTime;
                    checkin.BusId = busId;
                    checkin.Location = parts[3];
                    var lat = checkin.Location.Substring(0, checkin.Location.IndexOf('/'));
                    var lon = checkin.Location.Substring(checkin.Location.IndexOf('/') + 1);
                    lat = lat.Insert(lat.StartsWith("-") ? 3 : 2, ".");
                    lon = lon.Insert(lon.StartsWith("-") ? 3 : 2, ".");
                    checkin.Lat = double.Parse(lat);
                    checkin.Lon = double.Parse(lon);
                    checkin.LocationValid = parts[4] == "V";
                    checkin.Adherence = Int32.Parse(parts[5]);
                    checkin.AdherenceValid = parts[6] == "V";

                    int route;
                    if (parts.Length > 7 && Int32.TryParse(parts[7], out route))
                    {
                        checkin.HasRoute = true;
                        checkin.Route = route;
                        checkin.Direction = Int32.Parse(parts[8]);
                        int stopId;
                        checkin.StopId = Int32.TryParse(parts[9], out stopId) ? stopId : -1;
                    }
                    else
                    {
                        checkin.HasRoute = false;
                        checkin.Route = -1;
                        checkin.Direction = -1;
                        checkin.StopId = -1;
                    }

                    return checkin;
                }
            }

            return null;
        }
    }
}
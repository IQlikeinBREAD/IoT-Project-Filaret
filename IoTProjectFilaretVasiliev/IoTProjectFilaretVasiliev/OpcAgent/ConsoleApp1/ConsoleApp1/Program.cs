using Device;
using Microsoft.Azure.Devices.Client;

namespace ConsoleApp1
{
    internal class Program
    {
        static string deviceConnectionString = "HostName=IoT-uni-filaret6.azure-devices.net;DeviceId=Test-Device;SharedAccessKey=su85C/QkrwIfSsc+j1EX0KRGY/tD4VJcNAIoTAnvDlk=";
        static async Task Main(string[] args)
        {
            using var deviceClient = DeviceClient.CreateFromConnectionString(deviceConnectionString, TransportType.Mqtt);
            await deviceClient.OpenAsync();

            var device = new VirtualDevice(deviceClient);
            await device.InitializeHandlers();
            await device.UpdateTwinAsync();

            Console.WriteLine($"Connection success!");

            await device.SendMessages(10, 1000);

            Console.WriteLine("Finished! Press Enter to close...");
            Console.ReadLine();

        }
    }
}
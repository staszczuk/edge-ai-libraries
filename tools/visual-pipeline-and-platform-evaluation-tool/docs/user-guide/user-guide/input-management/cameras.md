# Cameras

This article explains how to use the Camera module in ViPPET to detect and connect to cameras.
From the left-side menu, choose **Cameras** to open the camera management page.

ViPPET supports three types of cameras: USB cameras, network cameras, and GenICam machine vision
cameras. USB cameras are detected automatically via plug-and-play, network cameras are discovered
using the ONVIF standard, and GenICam cameras are discovered using Aravis.

![Cameras](../../_assets/ViPPET-UI-Cameras-light.png)

## USB Cameras

Connecting a USB camera requires no additional configuration. Simply plug the camera into the host
machine. ViPPET automatically detects the device and displays it in the *Cameras* tab.

## Network Cameras

### Network camera discovery

Network cameras are discovered using the ONVIF standard. Before ViPPET can detect a network camera,
you must configure it correctly:

1. **Enable the ONVIF service** on the camera. Refer to the camera manufacturer's documentation for
   instructions on how to do this.
2. **Create an ONVIF media profile** on the camera, defining the desired stream settings (resolution,
   encoding, frame rate, and so on).
3. **Connect the camera to the same subnet** as the host machine running ViPPET. The Sensor Manager
   service uses multicast to find cameras, so the camera must be reachable within the local network
   segment.

Once the camera is properly configured and connected to the network, ViPPET automatically discovers
and displays it in the *Cameras* tab.

> [!NOTE]
> If a network camera does not appear in the *Cameras* tab, verify that the ONVIF service is
> enabled, a valid media profile exists, and the camera is on the same subnet as the host machine.

### Network camera authorization

After a network camera is discovered, authorization is required before it can be used. An *Authorize*
button appears next to the camera entry in the *Cameras* tab.

To authorize a camera:

1. Click the *Authorize* button next to the camera.
2. Enter the camera's *Username* and *Password*.
3. Confirm. If the credentials are accepted, the camera status changes to *Authorized*.

![Camera Authentication](../../_assets/ViPPET-UI-Cameras-Auth-light.png)

> [!NOTE]
> If authorization fails, verify that the username and password are correct, and ensure that
> the clock on the camera is synchronized with the clock on the host machine. Time skew between the
> camera and the host is a common cause of ONVIF authentication failures.

## GigE Vision Cameras

GenICam-compliant machine vision cameras (GigE Vision) are discovered by the Sensor Manager
service using Aravis and listed in the *Cameras* tab with the `GENICAM` type. The *Source* column
shows the camera IP address. No authorization is required.

Connect the camera to the same subnet as the host machine running ViPPET, so it can be reached by
GigE Vision discovery.

> [!NOTE]
> GenICam cameras are currently listed for discovery only and cannot be selected as pipeline
> input sources.

## Use cameras in pipelines as input sources

To use a camera as pipeline input, open the Pipeline Builder and click the **Input** block to see the properties.

![Pipeline Input](../../_assets/ViPPET-UI-Images-Pipeline-Input-light.png)

From the *Source Type* dropdown, select **Cameras**.

![Pipeline Source Type](../../_assets/ViPPET-UI-Cameras-Pipeline-Source-Type-light.png)

Then, from the *Source* dropdown, select the desired camera.

![Pipeline Source](../../_assets/ViPPET-UI-Cameras-Pipeline-Source-light.png)

The selected camera will now be used as the pipeline input.

> [!NOTE]
> A network camera that has not been authorized yet appears grayed out in the list and cannot
> be selected. To authorize the camera first, follow the steps in the
> [Network camera authorization](#network-camera-authorization) section.

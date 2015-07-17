## ConnectorC4D
Python Generator for Cinema 4D.
Gennerates splines to connect all targets in the list.
Mograph is treated as many individual objects of clones.

## Simple Usage
1. Select "User Data" tab of the Connector.
2. Add any objects to "Objects" list.
3. Set Max Distance to connect.

## Options
- Use Screen Distance: When this enabled, generator uses 2D Render View to calculate distances. Max distance : 1000 equals to screen width.
- Set Max Segments: Set maximum lines for each point.
- Use Center Object: Set this option when you want to connect all objects to single point.
- Exclude Lines in Same Group: When enabled, clones in the same mograph group are not connected.
- Step (in group): Increase this when you get too many lines. Works with mographs only.

## Make as preset
Select "Connector" inside example c4d file, and choose "File>Save Object Preset" to use in other scenes quickly.

## memo about Spline Settings
As all splines are segmented, Interpolation types are not useful...  
But subdivide settings works fine when you work with deformers.

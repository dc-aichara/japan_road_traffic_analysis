# Japan Road Traffic Analysis

## GPX Route Analysis and Road Status Visualization
This pipeline processes GPX route data to identify restricted or closed road sections and visually represents these sections on a map. It involves extracting road and prefecture information from the GPX file, retrieving road numbers and traffic status data, filtering for restricted roads, and finally plotting the route with any closed sections highlighted. This tool is useful for visualizing the accessibility of routes and planning alternate paths in case of road closures.

### Process Flow of gpx route analysis  and road status visualization


```mermaid
graph TD
    A[Start] --> B[get roads and prefecture codes using GPX file OSM data]
    B -->|roads, prefs| C[get road numbers using OSM data with Overpass API]
    C -->|road numbers| D{Loop: for each pref code in prefs}
    D --> E[get road status from JARTIC by prefecture code]
    E -->|traffic data| F{Loop: for each road number in road numbers}
    F --> G[filter traffic status by road]
    G -->|closed roads| H[filter roads for closed and restricteed roads]
    H -->|all affected roads, complete closed roads| I[plot route with closed sections]
    I -->|fig| J[Return all affected roads, fig]
```


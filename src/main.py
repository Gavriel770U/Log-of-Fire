from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re

def generate_pie_diagram_file(title: str, platforms_percentage: dict) -> None:
    html_code = """<!DOCTYPE HTML>
<html>
<head>
<script>
window.onload = function () {

var chart = new CanvasJS.Chart("chartContainer", {
	exportEnabled: true,
	animationEnabled: true,
	title:{
		text: \"""" + title + """\"
	},
	legend:{
		cursor: "pointer",
		itemclick: explodePie
	},
	data: [{
		type: "pie",
		showInLegend: true,
		toolTipContent: "{name}: <strong>{y}%</strong>",
		indexLabel: "{name} - {y}%",
		dataPoints: ["""

    sorted_platform_percentage = sorted(platforms_percentage, key=platforms_percentage.get, reverse=True)
    first = True
    for platform in sorted_platform_percentage:
        if first:
            stats_line = "{ y: " + str(platforms_percentage[platform]) + ", name: \"" + platform + "\", exploded: true },"
            first = False
        else:
            stats_line = "{ y: " + str(platforms_percentage[platform]) + ", name: \"" + platform + "\" },"
        html_code += stats_line
    
    
    html_code += """]
	}]
});
chart.render();
}

function explodePie (e) {
	if(typeof (e.dataSeries.dataPoints[e.dataPointIndex].exploded) === "undefined" || !e.dataSeries.dataPoints[e.dataPointIndex].exploded) {
		e.dataSeries.dataPoints[e.dataPointIndex].exploded = true;
	} else {
		e.dataSeries.dataPoints[e.dataPointIndex].exploded = false;
	}
	e.chart.render();

}
</script>
</head>
<body>
<div id="chartContainer" style="height: 300px; width: 100%;"></div>
<script src="https://cdn.canvasjs.com/canvasjs.min.js"></script>
</body>
</html>"""

    with open(f"{title}.html", "w") as file:
        file.write(html_code)


def generate_visits_per_hour_column_chart(title: str, visits_per_hour: dict) -> None:
    html_code = """<!DOCTYPE HTML>
<html>
<head>
<script>
window.onload = function () {

var chart = new CanvasJS.Chart("chartContainer", {
	animationEnabled: true,
	exportEnabled: true,
	theme: "light1", // "light1", "light2", "dark1", "dark2"
	title:{
		text: \"""" + title + """\"
	},
  	axisY: {
      includeZero: true
    },
	data: [{
		type: "column", //change type to bar, line, area, pie, etc
		//indexLabel: "{y}", //Shows y value on all Data Points
		indexLabelFontColor: "#5A5757",
      	indexLabelFontSize: 16,
		indexLabelPlacement: "outside",
		dataPoints: ["""
     
    for hour in visits_per_hour:
        stats_line = "{ x: " + str(hour) + ", y: " + str(visits_per_hour[hour]) + " },"
        html_code += stats_line
        
    html_code += """]
	}]
});
chart.render();

}
</script>
</head>
<body>
<div id="chartContainer" style="height: 300px; width: 100%;"></div>
<script src="https://cdn.canvasjs.com/canvasjs.min.js"></script>
</body>
</html>"""

    with open(f"{title}.html", "w") as file:
        file.write(html_code)


def generate_visits_per_day_in_month_graph(title: str, month: int, visits_per_day_in_month: dict) -> None:
    html_code = """<!DOCTYPE HTML>
<html>
<head>  
<script>
window.onload = function () {

var chart = new CanvasJS.Chart("chartContainer", {
	animationEnabled: true,
	title:{
		text: \"""" + title + """\"
	},
	axisX:{
		valueFormatString: "DD MMM",
		crosshair: {
			enabled: true,
			snapToDataPoint: true
		}
	},
	axisY: {
		crosshair: {
			enabled: true,
			snapToDataPoint: true,
		}
	},
	data: [{
		type: "area",
		xValueFormatString: "DD MMM",
		dataPoints: ["""

    # the month is month number - 1
    for day in visits_per_day_in_month:
        stats_line = "{ x: new Date(0, " + str(month - 1).zfill(2) + ", " + day + "), y: " + str(visits_per_day_in_month[day]) + " },"
        html_code += stats_line

    html_code += """]
	}]
});
chart.render();

}
</script>
</head>
<body>
<div id="chartContainer" style="height: 300px; width: 100%;"></div>
<script src="https://cdn.canvasjs.com/canvasjs.min.js"></script>
</body>
</html>"""

    with open(f"{title}.html", "w") as file:
        file.write(html_code)


def main() -> None:
    count_platforms = {
        "iPad" : 0,
        "iPhone" : 0,
        "Android" : 0,
        "Windows": 0,
    }
    
    MONTH_TO_DISPLAY_STATS: str = "Jan"
    MONTH_NUMBER: int = 1
    
    visits_per_hour = {}
    
    visits_per_day_in_month = {}
    
    for day in range(1, 32):
        visits_per_day_in_month[str(day).zfill(2)] = 0
    
    platform_percentage = {}
    
    zip_indexes = []
    for i in range(130101, 130132):
        zip_indexes.append(i)
    for i in range(130201, 130229):
        zip_indexes.append(i)
    for i in range(130301, 130307):
        zip_indexes.append(i)
    
    for zip_index in zip_indexes:
        resp = urlopen(f"http://firefire.cyber.org.il/logs/access_{zip_index}.zip")
        myzip = ZipFile(BytesIO(resp.read()))
        for line in myzip.open(f"access_{zip_index}.log").readlines():
            for platform in count_platforms.keys():
                if platform.lower() in line.decode('utf-8').lower():
                    count_platforms[platform] += 1
                    break

            pattern = r"\b\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}\b"
            match = re.search(pattern, line.decode('utf-8'))
            if match:
                hour = int(match.group().split(':')[1])
                if hour in visits_per_hour:
                    visits_per_hour[hour] += 1
                else:
                    visits_per_hour[hour] = 1
                    
                month = match.group().split('/')[1]
                day = match.group().split('/')[0]
                
                if MONTH_TO_DISPLAY_STATS == month:
                    if day in visits_per_day_in_month:
                        visits_per_day_in_month[day] += 1
                    else:
                        visits_per_day_in_month[day] = 1
    
    for platform in count_platforms.keys():
        platform_percentage[platform] = (count_platforms[platform] * 100) / sum(count_platforms.values())
        print(f"{platform}: {platform_percentage[platform]}%")
    
    generate_pie_diagram_file("Platforms Usage", platform_percentage)
    generate_visits_per_hour_column_chart("Visits Per Hour", visits_per_hour)
    generate_visits_per_day_in_month_graph("Daily Visits (January)", MONTH_NUMBER, visits_per_day_in_month)
    

if __name__ == "__main__":
    main()
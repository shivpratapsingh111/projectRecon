from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/api/subdomains', methods=['GET'])
def get_subdomains():
    response = {
        "tools": {
            "amass": {"subdomains_found": 120, "time_taken_seconds": 300},
            "subfinder": {"subdomains_found": 95, "time_taken_seconds": 250},
            "assetfinder": {"subdomains_found": 80, "time_taken_seconds": 200}
        },
        "total_subdomains_found": 295,
        "total_time_taken_seconds": 750
    }
    return jsonify(response)

@app.route('/api/urls', methods=['GET'])
def get_urls():
    response = {
        "tools": {
            "gau": {"urls_found": 500, "time_taken_seconds": 180},
            "wayback": {"urls_found": 450, "time_taken_seconds": 200},
            "hakrawler": {"urls_found": 300, "time_taken_seconds": 150}
        },
        "total_urls_found": 1250,
        "total_time_taken_seconds": 530
    }
    return jsonify(response)

@app.route('/api/summary', methods=['GET'])
def get_cummary():
    response = {
  "subdomains": {
    "tools": {
      "amass": {
        "subdomains_found": 120,
        "time_taken_seconds": 300
      },
      "subfinder": {
        "subdomains_found": 95,
        "time_taken_seconds": 250
      },
      "assetfinder": {
        "subdomains_found": 80,
        "time_taken_seconds": 200
      }
    },
    "total_subdomains_found": 295,
    "total_time_taken_seconds": 750
  },

  "urls": {
    "tools": {
      "gau": {
        "urls_found": 500,
        "time_taken_seconds": 180
      },
      "wayback": {
        "urls_found": 450,
        "time_taken_seconds": 200
      },
      "hakrawler": {
        "urls_found": 300,
        "time_taken_seconds": 150
      }
    },
    "total_urls_found": 1250,
    "total_time_taken_seconds": 530
  },
    "JS urls":
    {
        "scan_performed": True,
        "results":
        {
            "live_js_urls": 295,
            "not_live_js_urls": 100,
            "total_js_urls": 395
        }
    },

    "Nuclei":
    {
        "scan_performed": True,
        "results":
        {
            "total_vuln_found": 1250,
            "critical": 0,
            "high": 500,
            "medium": 500,
            "low": 250,
            "info": 0,
            "unkown": 0
        }
    },
    "Nmap":
    {
        "scan_performed": False,
        "results":
        {
        }
    }
}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

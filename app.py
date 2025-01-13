from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            alternatives = [x.strip() for x in request.form["alternatives"].split(",")]  
            weights = [float(x.strip()) for x in request.form["weights"].split(",")] 
            criteria_type = [x.strip() for x in request.form["criteria_type"].split(",")]  
            data = [x.strip() for x in request.form["data"].split("\n")]  

            if '' in alternatives or '' in weights or '' in criteria_type or '' in data:
                return "All input must be filled in bitchhh!", 400


            matrix = []
            for row in data:
                row_data = row.split(",")
                if '' in row_data:  
                    return "Alternative value data cannot be empty!", 400
                matrix.append(list(map(float, row_data)))  

            if len(weights) != len(matrix[0]):
                return "The number of weights does not match the number of criteria, ur fuckin stupid shit!", 400
            if len(criteria_type) != len(matrix[0]):
                return "The number of criteria types does not match the number of criteria, get it bitch?", 400

            ranked, scores = topsis(matrix, weights, criteria_type)

            result = {
                "ranked": ranked,
                "scores": scores,
                "alternatives": alternatives
            }

        except ValueError as e:
            return f"An error occurred in data conversion: {e}", 400

    return render_template("index.html", result=result, zip=zip)

def topsis(matrix, weights, criteria_type):
    import numpy as np
    
    matrix = np.array(matrix)
    norm_matrix = matrix / np.sqrt((matrix ** 2).sum(axis=0))
    weighted_matrix = norm_matrix * weights

    if criteria_type == 'max':
        ideal_positive = np.max(weighted_matrix, axis=0)
        ideal_negative = np.min(weighted_matrix, axis=0)
    else:
        ideal_positive = np.min(weighted_matrix, axis=0)
        ideal_negative = np.max(weighted_matrix, axis=0)

    distance_positive = np.sqrt(((weighted_matrix - ideal_positive) ** 2).sum(axis=1))
    distance_negative = np.sqrt(((weighted_matrix - ideal_negative) ** 2).sum(axis=1))

    scores = distance_negative / (distance_positive + distance_negative)
    ranked = np.argsort(scores)[::-1]

    return ranked, scores

if __name__ == "__main__":
    app.run(debug=True)

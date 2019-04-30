import responder
import json

api = responder.API()


@api.route("/")
def index(req, resp):
    resp.content = api.template("/home/index.html")


@api.route("/api/{beds_code}/{construction_spending}")
def index(req, resp, beds_code: str, construction_spending: str):
    # Prepare some metadata
    metadata = {"BEDS Code": beds_code,
                "Construction Spending": construction_spending}

    # Opent the model JSON data
    with open("data/model.json") as f:
        model = json.load(f)

    try:
        # Convert the data to a float
        construction_spending = float(construction_spending)
        # Find the row for the school district in question
        m = model[beds_code]
        metadata["School District"] = m["School District"].title()
        # All data in the model are per $1M spending so we need to scale the
        # calculations for our specific case
        scalar = construction_spending / 1000000
        # Create the API data
        data = {
            "jobs": {
                "direct": round(m["Direct Employment Estimate"] * scalar),
                "spillover": round(m["Indirect Employment Estimate"] * scalar),
            },
            "payroll": {
                "direct": round(m["Direct Payroll Estimate"] * scalar),
                "spillover": round(m["Indirect Payroll Estimate"] * scalar),
            },
            "income_tax": {
                "direct": round(m["Direct Income Tax Estimate"] * scalar),
                "spillover": round(m["Indirect Income Tax Estimate"] * scalar),
            },
            "sales_tax": {
                "direct": round(m["Direct Sales Tax Estimate"] * scalar),
                "spillover": round(m["Indirect Sales Tax Estimate"] * scalar),
            },
        }
        # Make total the sum of the components
        data["jobs"]["total"] = (
            data["jobs"]["direct"] + data["jobs"]["spillover"]
        )
        data["payroll"]["total"] = (
            data["payroll"]["direct"] + data["payroll"]["spillover"]
        )
        data["income_tax"]["total"] = (
            data["income_tax"]["direct"] + data["income_tax"]["spillover"]
        )
        data["sales_tax"]["total"] = (
            data["sales_tax"]["direct"] + data["sales_tax"]["spillover"]
        )

    except:
        data = None

    resp.media = {"data": data, "metadata": metadata}


api.run()

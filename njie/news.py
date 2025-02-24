import frappe

@frappe.whitelist(allow_guest=True)
def all(category=None):
    try:
        filters = {}
        if category:
            filters = {'blog_category': category}
        blogs = frappe.get_list('Blog Post', filters=filters)
        data = []

        for blog in blogs:
            doc = frappe.get_doc('Blog Post', blog.name)
            data.append({
                "id": doc.name,
                "title": doc.title,
                "published_on": doc.published_on,
                "blog_category": doc.blog_category,
                "blog_intro": doc.blog_intro,
                "blog_intro": doc.blog_intro,
                "content": doc.content,
                "image": frappe.utils.get_url(doc.meta_image) if doc.meta_image else "https://njie.royalsmb.com/files/njie%20harakha%20logo%20.jpg"
            })
        
        frappe.local.response.update({
            "http_status_code": 200,
            "data": data
        })
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Custom Error Log")
        frappe.local.response.update({
            "http_status_code": 500,
            "error": str(e)
        })
    

@frappe.whitelist(allow_guest=True)
def get(id:str):
    try:
        if not frappe.db.exists('Blog Post', id):
            raise Exception("Invalid Blog ID")
        doc = frappe.get_doc('Blog Post', id)
        frappe.local.response.update({
            "http_status_code": 200,
            "data": {
                "id": doc.name,
                "title": doc.title,
                "published_on": doc.published_on,
                "blog_category": doc.blog_category,
                "blog_intro": doc.blog_intro,
                "blog_intro": doc.blog_intro,
                "content": doc.content,
                "image": frappe.utils.get_url(doc.meta_image) if doc.meta_image else "https://njie.royalsmb.com/files/njie_harakha_logo_-removebg-preview.png"
            }
        })
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Custom Error Log")
        frappe.local.response.update({
            "http_status_code": 500,
            "error": str(e)
        })
   

from datetime import datetime

from flask import current_app, redirect, render_template, request, url_for
from flask_babel import lazy_gettext

from flaskshop.dashboard.forms import (
    AttributeForm,
    CategoryForm,
    CollectionForm,
    ProductCreateForm,
    ProductForm,
    ProductTypeForm,
    VariantForm,
)
from flaskshop.product.models import (
    Category,
    Collection,
    Product,
    ProductAttribute,
    ProductImage,
    ProductType,
    ProductVariant,
)
from flaskshop.dashboard.utils import save_img_file


def attributes():
    page = request.args.get("page", type=int, default=1)
    pagination = ProductAttribute.query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "values_label": lazy_gettext("Value"),
        "types_label": lazy_gettext("ProductType"),
    }
    context = {
        "title": lazy_gettext("Product Attribute"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "attributes",
    }
    return render_template("list.html", **context)


def attributes_manage(id=None):
    if id:
        attr = ProductAttribute.get_by_id(id)
        form = AttributeForm(obj=attr)
    else:
        attr = ProductAttribute()
        form = AttributeForm()
    form.product_types_ids.choices = [(p.id, p.title) for p in ProductType.query.all()]
    if form.validate_on_submit():
        attr.title = form.title.data
        attr.update_types(form.product_types_ids.data)
        attr.update_values(form.values_label.data.split(','))
        attr.save()
        return redirect(url_for("dashboard.attributes"))
    return render_template(
        "product/attribute.html", form=form
    )


def collections():
    page = request.args.get("page", type=int, default=1)
    pagination = Collection.query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "title": lazy_gettext("Product Collection"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "collections",
    }
    return render_template("list.html", **context)


def categories():
    page = request.args.get("page", type=int, default=1)
    pagination = Category.query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "parent": lazy_gettext("Parent"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "title": lazy_gettext("Product Category"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "categories",
    }
    return render_template("list.html", **context)


def collections_manage(id=None):
    if id:
        collection = Collection.get_by_id(id)
        form = CollectionForm(obj=collection)
    else:
        collection = Collection()
        form = CollectionForm()
    form.products_ids.choices = [(p.id, p.title) for p in Product.query.all()]
    if form.validate_on_submit():
        collection.title = form.title.data
        collection.update_products(form.products_ids.data)
        image = form.bgimg_file.data
        if image:
            collection.background_img = save_img_file(image)
        collection.save()
        return redirect(url_for("dashboard.collections"))
    return render_template("product/collection.html", form=form)


def categories_manage(id=None):
    if id:
        category = Category.get_by_id(id)
        form = CategoryForm(obj=category)
    else:
        category = Category()
        form = CategoryForm()
    form.parent_id.choices = [(c.id, c.title) for c in Category.first_level_items()]
    form.parent_id.choices.insert(0, (0, 'None'))
    if form.validate_on_submit():
        form.populate_obj(category)
        image = form.bgimg_file.data
        if image:
            category.background_img = save_img_file(image)
        category.save()
        return redirect(url_for("dashboard.categories"))
    return render_template("product/category.html", form=form)


def product_types():
    page = request.args.get("page", type=int, default=1)
    pagination = ProductType.query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "has_variants": lazy_gettext("Has Variants"),
        "is_shipping_required": lazy_gettext("Is Shipping Required"),
        "created_at": lazy_gettext("Created At"),
    }
    context = {
        "title": lazy_gettext("Product Type"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "product_types",
    }
    return render_template("list.html", **context)


def product_types_manage(id=None):
    if id:
        product_type = ProductType.get_by_id(id)
        form = ProductTypeForm(obj=product_type)
    else:
        form = ProductTypeForm()
    if form.validate_on_submit():
        if not id:
            product_type = ProductType()
        product_type.update_product_attr(form.product_attributes.data)
        product_type.update_variant_attr(form.variant_attr_id.data)
        del form.product_attributes
        del form.variant_attr_id
        form.populate_obj(product_type)
        product_type.save()
        return redirect(url_for("dashboard.product_types"))
    attributes = ProductAttribute.query.all()
    return render_template(
        "product/product_type.html", form=form, attributes=attributes
    )


def products():
    page = request.args.get("page", type=int, default=1)
    query = Product.query

    on_sale = request.args.get("sale", type=int)
    if on_sale is not None:
        query = query.filter_by(on_sale=on_sale)
    category = request.args.get("category", type=int)
    if category:
        query = query.filter_by(category_id=category)
    title = request.args.get("title", type=str)
    if title:
        query = query.filter(Product.title.like(f"%{title}%"))
    created_at = request.args.get("created_at", type=str)
    if created_at:
        query = query.filter(Product.created_at >= created_at)
    ended_at = request.args.get("ended_at", type=str)
    if ended_at:
        query = query.filter(Product.created_at <= ended_at)

    pagination = query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "on_sale_human": lazy_gettext("On Sale"),
        "sold_count": lazy_gettext("Sold Count"),
        "price_human": lazy_gettext("Price"),
        "category": lazy_gettext("Category"),
    }
    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "categories": Category.query.all(),
    }
    return render_template("product/list.html", **context)


def product_detail(id):
    product = Product.get_by_id(id)
    return render_template("product/detail.html", product=product)


def _save_product(product, form):
    # product.update_images(form.images.data)
    product.update_attributes(form.attributes.data)
    del form.images
    del form.attributes
    form.populate_obj(product)
    product.save()
    return product


def _save_new_images(product_id):
    upload_imgs = request.files.getlist("new_images")
    for img in upload_imgs:
        # request.files.getlist always not return empty, even not upload files
        if not img.filename:
            continue
        upload_path = current_app.config["UPLOAD_DIR"] / img.filename
        upload_path.write_bytes(img.read())
        ProductImage.create(
            image=upload_path.relative_to(current_app.config["STATIC_DIR"]).as_posix(),
            product_id=product_id,
        )


def product_edit(id):
    product = Product.get_by_id(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        _save_product(product, form)
        _save_new_images(product.id)
        return redirect(url_for("dashboard.product_detail", id=product.id))
    categories = Category.query.all()
    context = {"form": form, "categories": categories, "product": product}
    return render_template("product/product_edit.html", **context)


def product_create_step1():
    form = ProductCreateForm()
    form.product_type_id.choices = [(p.id, p.title) for p in ProductType.query.all()]
    if form.validate_on_submit():
        return redirect(
            url_for(
                "dashboard.product_create_step2",
                product_type_id=form.product_type_id.data,
            )
        )
    return render_template(
        "product/product_create_step1.html", form=form
    )


def product_create_step2():
    form = ProductForm()
    product_type_id = request.args.get("product_type_id", 1, int)
    product_type = ProductType.get_by_id(product_type_id)
    form.category_id.choices = [(c.id, c.title) for c in Category.query.all()]
    if form.validate_on_submit():
        product = Product(product_type_id=product_type_id)
        product = _save_product(product, form)
        _save_new_images(product.id)
        return redirect(url_for("dashboard.product_detail", id=product.id))
    return render_template(
        "product/product_create_step2.html",
        form=form,
        product_type=product_type,
    )


def variant_manage(id=None):
    if id:
        variant = ProductVariant.get_by_id(id)
        form = VariantForm(obj=variant)
    else:
        form = VariantForm()
    if form.validate_on_submit():
        if not id:
            variant = ProductVariant()
        form.populate_obj(variant)
        product_id = request.args.get("product_id")
        if product_id:
            variant.product_id = product_id
        variant.sku = str(variant.product_id) + "-" + str(form.sku_id.data)
        variant.save()
        return redirect(url_for("dashboard.product_detail", id=variant.product_id))
    return render_template("product/variant.html", form=form)

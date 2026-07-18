#!/usr/bin/env ruby
# frozen_string_literal: true

require 'fileutils'
require 'erb'
require 'json'
require 'nokogiri'
require 'gollum-lib'
require 'cgi'

ROOT = File.expand_path('..', __dir__)
OUTPUT = File.join(ROOT, '_site')
BASE_PATH = ENV.fetch('BASE_PATH', '/wiki').chomp('/')
SITE_URL = ENV.fetch('SITE_URL', 'https://giljae.github.io')
GITHUB_REPO = ENV.fetch('GITHUB_REPO', 'giljae/wiki')
GITHUB_BRANCH = ENV.fetch('GITHUB_BRANCH', 'main')
LAYOUT = File.join(ROOT, '_Layout.html')
SITE_NAME = "Giljae's Digital Garden"
SITE_DESCRIPTION = "#{SITE_NAME} — Gollum 기반 개인 위키"

SKIP_PAGES = %w[README 404].freeze
ASSET_PREFIXES = %w[assets].freeze

def page_slug(page)
  page.url_path.sub(/\.(md|markdown)$/i, '')
end

def normalize_path(path)
  path.to_s.sub(%r{\A/}, '').sub(/\.(md|markdown)$/i, '')
end

def static_href(path)
  normalized = normalize_path(path)
  return "#{BASE_PATH}/" if normalized.empty? || normalized == 'Home'

  "#{BASE_PATH}/#{normalized}/"
end

def canonical_url(path)
  "#{SITE_URL.chomp('/')}#{static_href(path)}"
end

def output_path(page)
  slug = page_slug(page)
  if slug == 'Home'
    File.join(OUTPUT, 'index.html')
  else
    File.join(OUTPUT, slug, 'index.html')
  end
end

def github_file_path(page)
  page.path
end

def github_edit_url(page)
  "https://github.com/#{GITHUB_REPO}/edit/#{GITHUB_BRANCH}/#{github_file_path(page)}"
end

def github_history_url(page)
  "https://github.com/#{GITHUB_REPO}/commits/#{GITHUB_BRANCH}/#{github_file_path(page)}"
end

def page_link?(path)
  return false if path.start_with?('#')
  return false if ASSET_PREFIXES.any? { |p| path.start_with?("#{p}/") }

  ext = File.extname(path)
  ext.empty? || ext.match?(/\.(md|markdown)$/i)
end

def rewrite_links(html)
  prefix = BASE_PATH.empty? ? '' : BASE_PATH

  html = html.gsub(%r{href="(#{Regexp.escape(prefix)})?/([^"#?]+)(#[^"]*)?"}m) do
    full = $&
    path = Regexp.last_match(2)
    fragment = Regexp.last_match(3) || ''
    next full if path.end_with?('/')
    next full unless page_link?(path)

    %(href="#{static_href(path)}#{fragment}")
  end

  html.gsub(%r{src="(#{Regexp.escape(prefix)})?/([^"]+)"}m) do
    path = Regexp.last_match(2)
    %(src="#{prefix}/#{path}")
  end
end

def plain_text(html)
  Nokogiri::HTML(html).text.gsub(/\s+/, ' ').strip
end

def page_description(page, html)
  text = plain_text(html)
  text.length > 160 ? "#{text[0, 157]}..." : text
end

def extract_toc_and_content(html)
  doc = Nokogiri::HTML.fragment(html)
  toc = doc.at_css('.toc')
  toc_html = toc ? toc.to_html : nil
  toc&.remove
  [doc.to_html, toc_html]
end

def build_breadcrumbs(slug, pages_by_slug)
  if slug == 'Home'
    return [{ label: 'Home', url: nil }]
  end

  crumbs = [{ label: 'Home', url: static_href('Home') }]

  parts = slug.split('/')
  parts.each_with_index do |_part, i|
    path_so_far = parts[0..i].join('/')
    page = pages_by_slug[path_so_far]
    label = page ? page.title : parts[i]
    url = (i == parts.length - 1) ? nil : static_href(path_so_far)
    crumbs << { label: label, url: url }
  end
  crumbs
end

def build_nav_tree(pages)
  root = {}
  pages.each do |page|
    slug = page_slug(page)
    parts = slug.split('/')
    node = root
    parts.each_with_index do |part, idx|
      node[part] ||= { 'children' => {}, 'page' => nil }
      node[part]['page'] = page if idx == parts.length - 1
      node = node[part]['children']
    end
  end
  root
end

def nav_page_title(node, key)
  node['page'] ? node['page'].title : key
end

def render_nav_tree(nodes, parent_slug = '')
  return '' if nodes.empty?

  items = nodes.sort_by { |key, _| key == 'Home' ? '' : key.downcase }.map do |key, node|
    full_slug = parent_slug.empty? ? key : "#{parent_slug}/#{key}"
    title = CGI.escapeHTML(nav_page_title(node, key))
    has_children = !node['children'].empty?

    if node['page']
      link = %(<a href="#{static_href(full_slug)}" data-slug="#{full_slug}">#{title}</a>)
    else
      link = %(<span class="nav-folder-label" data-slug="#{full_slug}">#{title}</span>)
    end

    child_html = has_children ? render_nav_tree(node['children'], full_slug) : ''
    %(<li class="nav-item#{has_children ? ' nav-has-children' : ''}" data-slug="#{full_slug}">#{link}#{child_html}</li>)
  end

  %(<ul class="nav-tree">#{items.join}</ul>)
end

def build_sidebar_html(wiki, pages)
  manual = wiki.page('_Sidebar')&.formatted_data
  tree = build_nav_tree(pages)
  tree_html = render_nav_tree(tree)

  parts = []
  parts << rewrite_links(manual) if manual
  parts << %(<div class="nav-section"><p class="nav-heading">문서 목록</p>#{tree_html}</div>)
  parts.join
end

def render_page(page, sidebar_html, footer_html, pages_by_slug)
  raw_html = page.formatted_data
  content, toc_html = extract_toc_and_content(raw_html)
  content = rewrite_links(content)

  sidebar = sidebar_html
  footer = footer_html ? rewrite_links(footer_html) : nil

  slug = page_slug(page)
  site_description = SITE_DESCRIPTION
  meta_description = page_description(page, content)
  canonical = canonical_url(slug)
  site_name = SITE_NAME
  breadcrumbs = build_breadcrumbs(slug, pages_by_slug)
  edit_url = github_edit_url(page)
  history_url = github_history_url(page)
  current_slug = slug
  toc_sidebar = toc_html

  template = ERB.new(File.read(LAYOUT))
  template.result(binding)
end

def copy_assets
  assets_dir = File.join(ROOT, 'assets')
  FileUtils.cp_r(assets_dir, OUTPUT) if File.directory?(assets_dir)

  custom = File.join(ROOT, 'custom.css')
  FileUtils.cp(custom, OUTPUT) if File.exist?(custom)
end

def build_search_index(pages)
  pages.map do |page|
    html = page.formatted_data
    slug = page_slug(page)
    {
      'title' => page.title,
      'url' => static_href(slug),
      'content' => plain_text(html)
    }
  end
end

def build_sitemap(pages)
  urls = pages.map do |page|
    slug = page_slug(page)
    <<~XML.strip
      <url>
        <loc>#{canonical_url(slug)}</loc>
        <lastmod>#{page.version&.authored_date&.strftime('%Y-%m-%d') || Time.now.strftime('%Y-%m-%d')}</lastmod>
      </url>
    XML
  end

  <<~XML
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    #{urls.join("\n")}
    </urlset>
  XML
end

def build_robots
  <<~ROBOTS
    User-agent: *
    Allow: /

    Sitemap: #{SITE_URL.chomp('/')}#{BASE_PATH}/sitemap.xml
  ROBOTS
end

FileUtils.rm_rf(OUTPUT)
FileUtils.mkdir_p(OUTPUT)

wiki = Gollum::Wiki.new(ROOT, base_path: "#{BASE_PATH}/", css: true, display_metadata: false)
footer_page = wiki.page('_Footer')
footer_html = footer_page&.formatted_data

pages = wiki.pages.reject(&:sub_page).reject { |p| SKIP_PAGES.include?(page_slug(p)) }
pages_by_slug = pages.to_h { |p| [page_slug(p), p] }
sidebar_html = build_sidebar_html(wiki, pages)

pages.each do |page|
  dest = output_path(page)
  FileUtils.mkdir_p(File.dirname(dest))
  File.write(dest, render_page(page, sidebar_html, footer_html, pages_by_slug))
  puts "  #{page.url_path} -> #{dest.sub(ROOT + '/', '')}"
end

error_page = wiki.page('404')
if error_page
  File.write(File.join(OUTPUT, '404.html'), render_page(error_page, sidebar_html, footer_html, pages_by_slug))
  puts '  404.md -> 404.html'
end

copy_assets
File.write(File.join(OUTPUT, 'search-index.json'), JSON.pretty_generate(build_search_index(pages)))
File.write(File.join(OUTPUT, 'sitemap.xml'), build_sitemap(pages))
File.write(File.join(OUTPUT, 'robots.txt'), build_robots)
puts '  search-index.json'
puts '  sitemap.xml'
puts '  robots.txt'
puts "\nBuilt #{pages.size} pages to #{OUTPUT}"

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

def clean_url_path(page)
  static_href(page_slug(page))
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

def render_page(page, sidebar_html, footer_html)
  content = rewrite_links(page.formatted_data)
  sidebar = sidebar_html
  footer = footer_html ? rewrite_links(footer_html) : nil

  site_description = SITE_DESCRIPTION
  meta_description = page_description(page, content)
  canonical = canonical_url(page_slug(page))
  site_name = SITE_NAME
  slug = page_slug(page)
  clean_url_path = static_href(slug)

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

def build_sidebar_html(wiki, pages)
  manual = wiki.page('_Sidebar')&.formatted_data
  return nil unless manual

  nav_pages = pages
    .sort_by { |p| page_slug(p).downcase }
    .map do |page|
      slug = page_slug(page)
      %(<li><a href="#{static_href(slug)}">#{CGI.escapeHTML(page.title)}</a></li>)
    end

  auto_nav = <<~HTML
    <p><strong>All Pages</strong></p>
    <ul>#{nav_pages.join}</ul>
  HTML

  "#{rewrite_links(manual)}#{auto_nav}"
end

FileUtils.rm_rf(OUTPUT)
FileUtils.mkdir_p(OUTPUT)

wiki = Gollum::Wiki.new(ROOT, base_path: "#{BASE_PATH}/", css: true, display_metadata: false)
footer_page = wiki.page('_Footer')
footer_html = footer_page&.formatted_data

pages = wiki.pages.reject(&:sub_page).reject { |p| SKIP_PAGES.include?(page_slug(p)) }
sidebar_html = build_sidebar_html(wiki, pages)

pages.each do |page|
  dest = output_path(page)
  FileUtils.mkdir_p(File.dirname(dest))
  File.write(dest, render_page(page, sidebar_html, footer_html))
  puts "  #{page.url_path} -> #{dest.sub(ROOT + '/', '')}"
end

# 404 page
error_page = wiki.page('404')
if error_page
  File.write(File.join(OUTPUT, '404.html'), render_page(error_page, sidebar_html, footer_html))
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

#!/usr/bin/env ruby
# frozen_string_literal: true

require 'fileutils'
require 'erb'
require 'json'
require 'nokogiri'
require 'gollum-lib'

ROOT = File.expand_path('..', __dir__)
OUTPUT = File.join(ROOT, '_site')
BASE_PATH = ENV.fetch('BASE_PATH', '/wiki').chomp('/')
LAYOUT = File.join(ROOT, '_Layout.html')
SITE_DESCRIPTION = "Giljae's Digital Garden — Gollum 기반 개인 위키"

SKIP_PAGES = %w[README].freeze

def page_slug(page)
  File.basename(page.url_path, File.extname(page.url_path))
end

def static_href(slug)
  if slug == 'Home'
    "#{BASE_PATH}/"
  else
    "#{BASE_PATH}/#{slug}.html"
  end
end

def output_path(page)
  slug = page_slug(page)
  if slug == 'Home'
    File.join(OUTPUT, 'index.html')
  else
    File.join(OUTPUT, "#{slug}.html")
  end
end

def rewrite_links(html)
  prefix = BASE_PATH.empty? ? '' : BASE_PATH

  html = html.gsub(%r{href="(#{Regexp.escape(prefix)})?/([^"#?]+)(#[^"]*)?"}m) do
    path = Regexp.last_match(2)
    fragment = Regexp.last_match(3) || ''
    slug = File.basename(path, File.extname(path))
    %(href="#{static_href(slug)}#{fragment}")
  end

  html.gsub(%r{src="(#{Regexp.escape(prefix)})?/([^"]+)"}m) do
    path = Regexp.last_match(2)
    %(src="#{prefix}/#{path}")
  end
end

def plain_text(html)
  Nokogiri::HTML(html).text.gsub(/\s+/, ' ').strip
end

def render_page(page, sidebar_html)
  content = page.formatted_data
  content = rewrite_links(content)

  sidebar = sidebar_html ? rewrite_links(sidebar_html) : nil
  site_description = SITE_DESCRIPTION

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
    {
      'title' => page.title,
      'url' => static_href(page_slug(page)),
      'content' => plain_text(html)
    }
  end
end

wiki = Gollum::Wiki.new(ROOT, base_path: "#{BASE_PATH}/", css: true, display_metadata: false)
sidebar_page = wiki.page('_Sidebar')
sidebar_html = sidebar_page&.formatted_data

FileUtils.rm_rf(OUTPUT)
FileUtils.mkdir_p(OUTPUT)

pages = wiki.pages.reject(&:sub_page).reject { |p| SKIP_PAGES.include?(page_slug(p)) }

pages.each do |page|
  dest = output_path(page)
  FileUtils.mkdir_p(File.dirname(dest))
  File.write(dest, render_page(page, sidebar_html))
  puts "  #{page.url_path} -> #{dest.sub(ROOT + '/', '')}"
end

copy_assets
File.write(File.join(OUTPUT, 'search-index.json'), JSON.pretty_generate(build_search_index(pages)))
puts "  search-index.json"
puts "\nBuilt #{pages.size} pages to #{OUTPUT}"

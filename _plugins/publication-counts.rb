require "bibtex"

module Jekyll
  class PublicationCounts < Generator
    safe true

    def generate(site)
      scholar = site.config.fetch("scholar")
      source = scholar.fetch("source").sub(%r{\A/}, "")
      bibliography = BibTeX.open(File.join(site.source, source, scholar.fetch("bibliography")))
      counts = Hash.new(0)
      yearly = Hash.new { |hash, key| hash[key] = Hash.new(0) }
      bibliography.entries.each_value do |entry|
        category = entry[:publication_type].to_s
        counts[category] += 1
        yearly[category][entry[:year].to_s.to_i] += 1
      end
      site.data["publication_counts"] = counts
      years = yearly.values.flat_map(&:keys).uniq.sort
      years = (years.first..years.last).to_a unless years.empty?
      maximum = yearly.values.flat_map(&:values).max || 1
      rows = site.data.fetch("publication_categories").keys.map do |category|
        cells = years.map do |year|
          count = yearly[category][year]
          { "year" => year, "count" => count, "opacity" => count.zero? ? 0 : (0.2 + 0.8 * count / maximum.to_f).round(2) }
        end
        { "category" => category, "total" => counts[category], "cells" => cells }
      end
      site.data["publication_activity"] = { "years" => years, "rows" => rows, "total" => counts.values.sum }
    end
  end
end

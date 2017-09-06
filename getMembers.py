#!/usr/bin/env python

import json
import requests
from optparse import OptionParser

def main():
  members = []
  parser = OptionParser(usage="Usage: %prog [options] filename",
                        version="%prog 1.0")

  parser.add_option("-o", "--org",
                    dest="org_name",
                    default="",
                    help="github org name to query")

  parser.add_option("-t", "--token",
                    dest="auth_token",
                    default=False,
                    help="github access token. https://github.com/settings/tokens")

  (options, args) = parser.parse_args()

  if options.auth_token != False:

    graphQLFirstQuery = (
      "query {",
      "organization(login:\"{Organization}\") {{".format(Organization=options.org_name),
      "  name",
      "  organizationBillingEmail",
      "  members (first:100) {",
      "    pageInfo {",
      "      endCursor",
      "      hasNextPage",
      "      hasPreviousPage",
      "      startCursor",
      "    }",
      "    nodes {",
      "      id",
      "      avatarUrl",
      "      login",
      "      email",
      "      name",
      "    }",
      "  }",
      "}}"
    )
    query = " ".join(graphQLFirstQuery)
    data = json.dumps({
      "query": query
    })

    r = requests.post("https://api.github.com/graphql",
                      headers={'Authorization': 'bearer {token}'.format(token=options.auth_token)},
                      data=data
        )

    next_cursor = ""

    response = json.loads(r.text)
    hasPageContent=True
    while r.status_code == 200 and hasPageContent == True:
      next_cursor = response["data"]["organization"]["members"]["pageInfo"]["endCursor"]
      members = members + response["data"]["organization"]["members"]["nodes"]
      hasPageContent = response["data"]["organization"]["members"]["pageInfo"]["hasNextPage"]

      graphQLPageQuery = (
        "query {",
        "organization(login:\"{Organization}\") {{".format(Organization=options.org_name),
        "  name",
        "  organizationBillingEmail",
        "  members (first:100,after:\"{NextCursor}\") {{".format(NextCursor=next_cursor),
        "    pageInfo {",
        "      endCursor",
        "      hasNextPage",
        "      hasPreviousPage",
        "      startCursor",
        "    }",
        "    nodes {",
        "      id",
        "      avatarUrl",
        "      login",
        "      email",
        "      name",
        "    }",
        "  }",
        "}}"
      )
      query = " ".join(graphQLPageQuery)
      data = json.dumps({
        "query": query
      })
      r = requests.post("https://api.github.com/graphql",
                        headers={'Authorization': 'bearer {token}'.format(token=options.auth_token)},
                        data=data
          )
      response = json.loads(r.text)




    for member in members:
      try:
        print "{login}\t{avatarUrl}\t{email}\t{name}".format(
          login=member["login"].decode('utf-8'),
          avatarUrl=member["avatarUrl"].decode('utf-8'),
          name=member["name"].decode('utf-8'),
          email=member["email"].decode('utf-8'))
      except:
        print "{login}\t{avatarUrl}\t{email}".format(
          login=member["login"].decode('utf-8'),
          avatarUrl=member["avatarUrl"].decode('utf-8'),
          name="DecodeError",
          email=member["email"].decode('utf-8'))




if __name__ == '__main__':
  main()
